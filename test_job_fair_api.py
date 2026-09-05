"""
Integration tests for Dynamic Job Fair & Events Banner Management and Public APIs.
"""
import unittest
import json
import sqlite3
import os
import server

class TestDynamicJobFairAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()
        server.init_database()

    def get_admin_token(self, email="mack.chen@viccollege.com", password="admin123"):
        res = self.client.post('/api/auth/login', json={
            'email': email,
            'password': password
        })
        data = res.get_json() or {}
        self.assertIn('token', data, f"Admin login must return token. Got response: {data}")
        return data['token']

    def test_01_public_active_job_fair(self):
        """Test public GET /api/job-fair returns the currently active job fair event."""
        res = self.client.get('/api/job-fair')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_active'])
        self.assertIsNotNone(data['job_fair'])
        jf = data['job_fair']
        self.assertIn('IN-PERSON PSW JOB FAIR', jf['title_en'])
        self.assertIn('维多利亚线下', jf['title_zh'])
        self.assertEqual(jf['btn_text_en'], 'Secure Your Spot')

    def test_02_admin_job_fair_crud_lifecycle(self):
        """Test complete Admin CRUD lifecycle for Job Fair events."""
        token = self.get_admin_token()
        headers = {'Authorization': f'Bearer {token}'}

        # 1. List all job fairs
        res = self.client.get('/api/admin/job-fairs', headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['job_fairs']), 1)

        # 2. Create new job fair event
        new_event = {
            'tag_en': 'Fall Career Mega Fair',
            'tag_zh': '秋季大型就业招聘节',
            'title_en': '2026 GTA Tech & Healthcare Career Mega Fair',
            'title_zh': '2026大多伦多地区科技与医疗高薪招聘盛会',
            'subtitle_en': 'Meet 40+ hiring managers and get hired on the spot.',
            'subtitle_zh': '40+ 名企雇主现场直聘，高薪全职岗位即刻锁定。',
            'date_en': 'Saturday, 25 October | 10:00AM – 4:00PM',
            'date_zh': '10月25日 周六 上午 10:00 – 下午 4:00',
            'location_en': '7050 Woodbine Ave. Unit 300, Markham',
            'location_zh': '7050 Woodbine Ave. Unit 300, Markham',
            'btn_text_en': 'Register Free Pass',
            'btn_text_zh': '立即免费抢票',
            'btn_link': '#consultation',
            'bg_image_url': 'images/job-fair.png',
            'is_active': 1
        }

        create_res = self.client.post('/api/admin/job-fairs', json=new_event, headers=headers)
        self.assertEqual(create_res.status_code, 201)
        created_data = create_res.get_json()
        self.assertTrue(created_data['success'])
        created_id = created_data['job_fair']['id']

        # 3. Verify it is now the active banner on public site
        pub_res = self.client.get('/api/job-fair')
        pub_data = pub_res.get_json()
        self.assertTrue(pub_data['success'])
        self.assertEqual(pub_data['job_fair']['id'], created_id)
        self.assertEqual(pub_data['job_fair']['title_en'], new_event['title_en'])

        # 4. Update the event
        update_payload = {
            'title_en': '2026 GTA Tech & Healthcare Mega Fair (Updated)',
            'location_en': 'Markham Convention Center, 7050 Woodbine Ave.'
        }
        update_res = self.client.put(f'/api/admin/job-fairs/{created_id}', json=update_payload, headers=headers)
        self.assertEqual(update_res.status_code, 200)
        updated_data = update_res.get_json()
        self.assertEqual(updated_data['job_fair']['title_en'], update_payload['title_en'])

        # 5. Toggle status to inactive
        toggle_res = self.client.patch(f'/api/admin/job-fairs/{created_id}/toggle-status', headers=headers)
        self.assertEqual(toggle_res.status_code, 200)
        toggle_data = toggle_res.get_json()
        self.assertEqual(toggle_data['is_active'], 0)

        # 6. Verify public API returns null/inactive
        pub_res2 = self.client.get('/api/job-fair')
        pub_data2 = pub_res2.get_json()
        self.assertFalse(pub_data2['is_active'])
        self.assertIsNone(pub_data2['job_fair'])

        # 7. Delete the created event
        del_res = self.client.delete(f'/api/admin/job-fairs/{created_id}', headers=headers)
        self.assertEqual(del_res.status_code, 200)

        # 8. Re-activate default job fair
        res_list = self.client.get('/api/admin/job-fairs', headers=headers)
        all_jf = res_list.get_json()['job_fairs']
        if all_jf:
            first_id = all_jf[0]['id']
            self.client.patch(f'/api/admin/job-fairs/{first_id}/toggle-status', headers=headers)

    def test_03_admin_stats_job_fair(self):
        """Test that /api/admin/stats includes job fair metrics."""
        token = self.get_admin_token()
        res = self.client.get('/api/admin/stats', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total_job_fairs', data)
        self.assertIn('active_job_fairs', data)
        self.assertIn('job_fair_active', data)
        self.assertIsInstance(data['job_fair_active'], bool)

if __name__ == '__main__':
    unittest.main()
