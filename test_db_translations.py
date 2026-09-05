import unittest
import json
import sqlite3
import os
from server import app, DB_PATH, create_user_session, init_database

class TestDatabaseTranslations(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        init_database()
        with app.app_context():
            self.admin_token = create_user_session(1)

    def test_database_has_translations(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM site_translations")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertGreater(count, 150, "Expected at least 150 translation keys in database")

    def test_public_translations_endpoint(self):
        res = self.app.get('/api/translations')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('en', data)
        self.assertIn('zh', data)
        self.assertIn('topbar_call', data['en'])
        self.assertIn('topbar_call', data['zh'])
        self.assertEqual(data['en']['topbar_call'], 'Call Us: 416-665-6668')
        self.assertEqual(data['zh']['topbar_call'], '咨询热线: 416-665-6668')

    def test_admin_translations_list(self):
        res = self.app.get('/api/admin/translations', headers={'Authorization': f'Bearer {self.admin_token}'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('translations', data)
        self.assertGreater(len(data['translations']), 100)

    def test_admin_update_translation(self):
        key = 'topbar_call'
        new_en = 'Call Us: 416-665-6668 (Toll Free)'
        new_zh = '咨询专线: 416-665-6668 (免费评估)'

        res = self.app.put(f'/api/admin/translations/{key}', 
                           headers={'Authorization': f'Bearer {self.admin_token}'},
                           json={'text_en': new_en, 'text_zh': new_zh})
        self.assertEqual(res.status_code, 200)

        # Verify public API returns updated text
        pub_res = self.app.get('/api/translations')
        pub_data = pub_res.get_json()
        self.assertEqual(pub_data['en'][key], new_en)
        self.assertEqual(pub_data['zh'][key], new_zh)

        # Reset back
        self.app.put(f'/api/admin/translations/{key}', 
                     headers={'Authorization': f'Bearer {self.admin_token}'},
                     json={'text_en': 'Call Us: 416-665-6668', 'text_zh': '咨询热线: 416-665-6668'})

if __name__ == '__main__':
    unittest.main()
