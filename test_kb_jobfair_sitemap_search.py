import unittest
import json
import xml.etree.ElementTree as ET
from server import (
    app, init_database, get_db,
    search_knowledge_base, search_job_fairs, build_sitemap_xml
)

class TestKBJobFairSitemapSearch(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        init_database()

    def _get_admin_token(self):
        res = self.app.post('/api/auth/login', json={
            'email': 'mack.chen@viccollege.com',
            'password': 'admin123'
        })
        data = res.get_json() or {}
        self.assertIn('token', data, f"Login failed: {data}")
        return data['token']

    def test_01_knowledge_base_search_includes_inactive(self):
        unique_term = "SpecializedRoboticsCertificate2026"
        with app.app_context():
            db = get_db()
            cursor = db.cursor()

            # Insert a unique inactive knowledge article
            cursor.execute("""
                INSERT INTO knowledge_base (category, title, keywords, content, priority, is_active, created_at, updated_at)
                VALUES ('programs', 'Advanced Robotics Training Program', 'robotics, automation, SpecializedRoboticsCertificate2026', 'Comprehensive robotics certificate program details.', 2, 0, '2026-09-25T00:00:00', '2026-09-25T00:00:00')
            """)
            db.commit()
            kb_id = cursor.lastrowid

            # 1. Direct function search
            direct_matches = search_knowledge_base(unique_term, include_inactive=True)
            self.assertTrue(any(m['id'] == kb_id for m in direct_matches), "Direct KB search did not find inactive article")

        # 2. Dedicated public search endpoint
        res = self.app.get(f'/api/knowledge/search?q={unique_term}')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(any(m['id'] == kb_id for m in data['results']), "Public KB search did not find inactive article")
        matched = next(m for m in data['results'] if m['id'] == kb_id)
        self.assertEqual(matched['is_active'], 0)

        # 3. Unified multi-entity search endpoint
        res = self.app.get(f'/api/search?q={unique_term}')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('knowledge_base', data['results'])
        self.assertTrue(any(m['id'] == kb_id for m in data['results']['knowledge_base']), "Unified search did not find inactive KB article")

        # 4. Admin Knowledge search and status filter
        token = self._get_admin_token()
        res = self.app.get(f'/api/admin/knowledge?search={unique_term}&status=inactive', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(res.status_code, 200)
        admin_data = res.get_json()
        self.assertTrue(any(a['id'] == kb_id for a in admin_data['articles']))

        # 5. Toggle status endpoint
        toggle_res = self.app.patch(f'/api/admin/knowledge/{kb_id}/toggle-status', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(toggle_res.status_code, 200)
        toggle_data = toggle_res.get_json()
        self.assertTrue(toggle_data['success'])
        self.assertEqual(toggle_data['is_active'], 1)

        # Clean up
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM knowledge_base WHERE id = ?", (kb_id,))
            db.commit()

    def test_02_job_fair_search_includes_inactive(self):
        unique_term = "GlobalBioTechCareerSummit2026"
        with app.app_context():
            db = get_db()
            cursor = db.cursor()

            # Insert a unique inactive job fair event
            cursor.execute("""
                INSERT INTO job_fairs (bg_image_url, btn_link, is_active, tag_en, title_en, subtitle_en, date_en, location_en, btn_text_en, tag_zh, title_zh, subtitle_zh, date_zh, location_zh, btn_text_zh, created_at, updated_at)
                VALUES ('images/job-fair.png', '#consultation', 0, 'SUMMIT', 'Global BioTech Career Expo', 'Connect with pharma employers and GlobalBioTechCareerSummit2026', 'Saturday, 20 June 2026', 'Markham Campus', 'Register Now', '峰会', '全球生物科技招聘博览会', '对接生物医药雇主', '2026年6月20日', '万锦校区', '立即报名', '2026-09-25T00:00:00', '2026-09-25T00:00:00')
            """)
            db.commit()
            jf_id = cursor.lastrowid

            # 1. Direct function search
            direct_matches = search_job_fairs(unique_term, include_inactive=True)
            self.assertTrue(any(m['id'] == jf_id for m in direct_matches), "Direct Job Fair search did not find inactive event")

        # 2. Dedicated public search endpoint
        res = self.app.get(f'/api/job-fairs/search?q={unique_term}')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(any(m['id'] == jf_id for m in data['results']), "Public Job Fair search did not find inactive event")
        matched = next(m for m in data['results'] if m['id'] == jf_id)
        self.assertEqual(matched['is_active'], 0)

        # 3. Unified multi-entity search endpoint
        res = self.app.get(f'/api/search?q={unique_term}')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('job_fairs', data['results'])
        self.assertTrue(any(m['id'] == jf_id for m in data['results']['job_fairs']), "Unified search did not find inactive Job Fair event")

        # 4. Admin Job Fairs search and status filter
        token = self._get_admin_token()
        res = self.app.get(f'/api/admin/job-fairs?search={unique_term}&status=inactive', headers={
            'Authorization': f'Bearer {token}'
        })
        self.assertEqual(res.status_code, 200)
        admin_data = res.get_json()
        self.assertTrue(any(e['id'] == jf_id for e in admin_data['job_fairs']))

        # Clean up
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM job_fairs WHERE id = ?", (jf_id,))
            db.commit()

    def test_03_sitemap_xml_generation(self):
        with app.app_context():
            # 1. Build sitemap string
            xml_content = build_sitemap_xml()
            self.assertIsInstance(xml_content, str)
            self.assertTrue(xml_content.startswith('<?xml version="1.0" encoding="UTF-8"?>'))

            # 2. Parse XML to ensure validity
            root = ET.fromstring(xml_content)
            urls = [elem.text for elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            
            # Verify Core Pages
            self.assertIn('https://viccollege.ca/', urls)
            self.assertIn('https://viccollege.ca/#programs', urls)
            self.assertIn('https://viccollege.ca/#financial-aid', urls)
            self.assertIn('https://viccollege.ca/#about', urls)
            self.assertIn('https://viccollege.ca/#consultation', urls)

            # Verify Academic Programs
            self.assertIn('https://viccollege.ca/personal-support-worker-online-psw-course.html', urls)
            self.assertIn('https://viccollege.ca/software-development.html', urls)
            self.assertIn('https://viccollege.ca/computerized-accounting.html', urls)

            # Verify Compliance & Policy Pages
            self.assertIn('https://viccollege.ca/sexual-violence-policy.html', urls)
            self.assertIn('https://viccollege.ca/students-complaint-procedure.html', urls)

            # Verify Job Fair section & event deep links
            self.assertIn('https://viccollege.ca/#job-fair', urls)
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT id FROM job_fairs")
            jf_rows = cursor.fetchall()
            for r in jf_rows:
                self.assertIn(f'https://viccollege.ca/#job-fair-event-{r["id"]}', urls)

            # Verify Knowledge Base hub & article deep links
            self.assertIn('https://viccollege.ca/#knowledge-base', urls)
            cursor.execute("SELECT id FROM knowledge_base")
            kb_rows = cursor.fetchall()
            for r in kb_rows:
                self.assertIn(f'https://viccollege.ca/article.html?kb={r["id"]}', urls)

        # 3. Test GET /sitemap.xml endpoint
        res = self.app.get('/sitemap.xml')
        self.assertEqual(res.status_code, 200)
        self.assertIn('application/xml', res.headers.get('Content-Type', ''))
        self.assertIn('<urlset', res.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
