"""
Automated Test Suite for Dynamic Homepage Sections CMS
Verifies Public & Admin API endpoints, SQLite persistence, authentication guards, and CRUD workflows.
"""
import unittest
import json
import sqlite3
from datetime import datetime, timedelta
from server import app, DB_PATH, init_database, create_user_session

class TestHomepageCMS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_database()

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Generate tokens from database sessions
        with app.app_context():
            # Admin user ID 1 (Mack Chen)
            self.admin_token = create_user_session(1)

            # Create/ensure a student test user
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM homepage_sections WHERE section_key LIKE 'test_%'")
            cursor.execute("SELECT id FROM users WHERE email = 'student_test@viccollege.com'")
            row = cursor.fetchone()
            if row:
                user_id = row[0]
            else:
                cursor.execute("""
                INSERT INTO users (email, name, role, password_hash, created_at)
                VALUES ('student_test@viccollege.com', 'Student Test', 'user', 'hash', datetime('now'))
                """)
                user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            self.user_token = create_user_session(user_id)

    def test_01_public_sections_api(self):
        """Test public API returns only active sections sorted by order_index"""
        res = self.app.get('/api/homepage/sections')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('sections', data)
        self.assertGreaterEqual(len(data['sections']), 8)
        
        # Verify ordering
        orders = [s['order_index'] for s in data['sections']]
        self.assertEqual(orders, sorted(orders))

        # Check default hero section presence
        hero = next((s for s in data['sections'] if s['section_key'] == 'hero'), None)
        self.assertIsNotNone(hero)
        self.assertEqual(hero['category'], 'hero')
        self.assertTrue(bool(hero['title_en']))
        self.assertTrue(bool(hero['title_zh']))

    def test_02_admin_guard_protection(self):
        """Test unauthenticated and non-admin requests are rejected"""
        # Unauthenticated GET
        res = self.app.get('/api/admin/homepage/sections')
        self.assertEqual(res.status_code, 401)

        # Non-admin token GET
        res = self.app.get('/api/admin/homepage/sections', headers={
            'Authorization': f'Bearer {self.user_token}'
        })
        self.assertEqual(res.status_code, 403)

        # Non-admin POST
        res = self.app.post('/api/admin/homepage/sections', headers={
            'Authorization': f'Bearer {self.user_token}'
        }, json={'section_key': 'hack', 'section_name': 'Hack'})
        self.assertEqual(res.status_code, 403)

    def test_03_admin_create_update_toggle_delete_flow(self):
        """Test full Admin CMS lifecycle: Create, Update, Toggle, Delete"""
        headers = {'Authorization': f'Bearer {self.admin_token}'}

        # 1. Create a custom promo section
        create_payload = {
            'section_key': 'test_summer_camp_2026',
            'section_name': 'Summer 2026 Tech BootCamp Banner',
            'category': 'custom',
            'title_en': 'Summer 2026 High-Tech Career Acceleration',
            'title_zh': '2026 暑期高薪 IT 极速就业实战营',
            'subtitle_en': 'Fast-track your IT skills with live enterprise labs.',
            'subtitle_zh': '名企导师带队，全真商业项目实战。',
            'badge_en': 'SPECIAL EVENT',
            'badge_zh': '特别活动',
            'content_en': '<p>Join 100+ graduates in AI & Web Engineering.</p>',
            'content_zh': '<p>前沿 AI 与 全栈开发实战培训。</p>',
            'cta_text_en': 'Register for Camp',
            'cta_text_zh': '立即报名实战营',
            'cta_link': '#consultation',
            'image_url': 'images/banner_bootcamp.jpg',
            'order_index': 99,
            'is_active': True
        }

        res = self.app.post('/api/admin/homepage/sections', headers=headers, json=create_payload)
        self.assertEqual(res.status_code, 201)
        created_data = json.loads(res.data)
        sec_id = created_data['id']
        self.assertTrue(sec_id > 0)

        # 2. Verify section is retrieved in Admin GET by ID
        res = self.app.get(f'/api/admin/homepage/sections/{sec_id}', headers=headers)
        self.assertEqual(res.status_code, 200)
        sec_data = json.loads(res.data)['section']
        self.assertEqual(sec_data['section_key'], 'test_summer_camp_2026')
        self.assertEqual(sec_data['title_en'], 'Summer 2026 High-Tech Career Acceleration')

        # 3. Update section
        update_payload = {
            'section_name': 'Summer 2026 Updated Tech BootCamp',
            'title_en': 'Updated Summer 2026 Fast-Track Bootcamp',
            'order_index': 100
        }
        res = self.app.put(f'/api/admin/homepage/sections/{sec_id}', headers=headers, json=update_payload)
        self.assertEqual(res.status_code, 200)
        
        # Verify update in DB
        res = self.app.get(f'/api/admin/homepage/sections/{sec_id}', headers=headers)
        sec_data = json.loads(res.data)['section']
        self.assertEqual(sec_data['title_en'], 'Updated Summer 2026 Fast-Track Bootcamp')
        self.assertEqual(sec_data['order_index'], 100)

        # 4. Toggle Active Status (Active -> Inactive)
        res = self.app.patch(f'/api/admin/homepage/sections/{sec_id}/toggle', headers=headers)
        self.assertEqual(res.status_code, 200)
        toggle_data = json.loads(res.data)
        self.assertFalse(toggle_data['is_active'])

        # Verify it disappears from public API
        pub_res = self.app.get('/api/homepage/sections')
        pub_sections = json.loads(pub_res.data)['sections']
        self.assertIsNone(next((s for s in pub_sections if s['id'] == sec_id), None))

        # 5. Delete Section
        res = self.app.delete(f'/api/admin/homepage/sections/{sec_id}', headers=headers)
        self.assertEqual(res.status_code, 200)

        # Verify section no longer exists
        res = self.app.get(f'/api/admin/homepage/sections/{sec_id}', headers=headers)
        self.assertEqual(res.status_code, 404)

    def test_04_admin_reorder_sections(self):
        """Test reordering sections updates database order indices"""
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        
        reorder_payload = {
            'orders': [
                {'id': 1, 'order_index': 10},
                {'id': 2, 'order_index': 20}
            ]
        }
        res = self.app.post('/api/admin/homepage/sections/reorder', headers=headers, json=reorder_payload)
        self.assertEqual(res.status_code, 200)

        # Reset back
        self.app.post('/api/admin/homepage/sections/reorder', headers=headers, json={
            'orders': [
                {'id': 1, 'order_index': 1},
                {'id': 2, 'order_index': 2}
            ]
        })

if __name__ == '__main__':
    unittest.main()
