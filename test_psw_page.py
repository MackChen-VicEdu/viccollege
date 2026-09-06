"""
Integration and End-to-End Link Verification Tests for Dynamic PSW Page and Homepage Integration.
"""
import unittest
import server

class TestPswPageIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()
        server.init_database()

    def test_01_psw_html_page_served_and_structured(self):
        """Verify personal-support-worker-online-psw-course.html serves 200 and has dynamic IDs."""
        res = self.client.get('/personal-support-worker-online-psw-course.html')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        
        # Check dynamic target IDs
        self.assertIn('id="psw-hero-badge"', html)
        self.assertIn('id="psw-hero-title"', html)
        self.assertIn('id="psw-hero-lead"', html)
        self.assertIn('id="psw-stat-1-val"', html)
        self.assertIn('id="psw-why-title"', html)
        self.assertIn('id="psw-pillars-grid"', html)
        self.assertIn('id="psw-cred-title"', html)
        self.assertIn('id="psw-credentials-grid"', html)
        self.assertIn('id="psw-curriculum-list"', html)
        self.assertIn('id="psw-prac-title"', html)
        self.assertIn('id="psw-prac-desc"', html)
        self.assertIn('id="psw-prac-box-title"', html)
        self.assertIn('id="psw-adm-title"', html)
        self.assertIn('id="psw-admissions-list"', html)
        self.assertIn('id="psw-faq-list"', html)
        self.assertIn('id="psw-side-credential"', html)
        self.assertIn('id="psw-side-duration"', html)
        self.assertIn('id="psw-side-delivery"', html)
        self.assertIn('id="psw-side-practicum"', html)
        self.assertIn('id="psw-side-locations"', html)
        self.assertIn('id="psw-side-hotline"', html)
        self.assertIn('id="psw-side-grant-badge"', html)
        self.assertIn('id="psw-nav-dropdown"', html)
        self.assertIn('id="psw-footer-prog-list"', html)
        self.assertIn('id="psw-bread-curr"', html)
        
        # Check dynamic hydration functions in script
        self.assertIn('loadPswPageDynamicData', html)
        self.assertIn('renderDynamicPswContent', html)
        self.assertIn('renderDynamicNavPrograms', html)
        self.assertIn('/api/programs/psw', html)
        self.assertIn('/api/programs', html)

    def test_02_index_html_cross_links_to_psw_page(self):
        """Verify index.html contains direct links to the dedicated PSW landing page."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')

        # Dropdown link
        self.assertIn('<a href="personal-support-worker-online-psw-course.html" data-i18n="prog_psw_title">NACC Personal Support Worker DE 2022</a>', html)
        
        # Program card links (image, heading, button)
        self.assertIn('<a href="personal-support-worker-online-psw-course.html" aria-label="NACC Personal Support Worker Program Details">', html)
        self.assertIn('<a href="personal-support-worker-online-psw-course.html" style="color: inherit; text-decoration: none;" data-i18n="prog_psw_title">NACC Personal Support Worker DE 2022</a>', html)
        self.assertIn('<a href="personal-support-worker-online-psw-course.html" class="btn-learn-more">', html)

        # Footer link
        self.assertIn('<li><a href="personal-support-worker-online-psw-course.html" data-i18n="prog_psw_title">NACC Personal Support Worker DE 2022</a></li>', html)

    def test_03_psw_api_endpoint_integrity(self):
        """Verify /api/programs/psw returns full bilingual data with detail_json for dynamic hydration."""
        res = self.client.get('/api/programs/psw')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        prog = data['program']

        self.assertEqual(prog['slug'], 'psw')
        self.assertIn('NACC', prog['title_en'])
        self.assertIn('PSW', prog['title_zh'])
        self.assertIn('23', prog['duration_en'])
        self.assertIn('23', prog['duration_zh'])
        self.assertIsNotNone(prog['overview_en'])
        self.assertIsNotNone(prog['overview_zh'])
        self.assertIsNotNone(prog['credential_en'])
        self.assertIsNotNone(prog['credential_zh'])

        # Verify detail_json_en structure
        detail_en = prog.get('detail_json_en') or {}
        self.assertIn('hero', detail_en)
        self.assertIn('stats', detail_en)
        self.assertGreaterEqual(len(detail_en['stats']), 4)
        self.assertIn('why_choose', detail_en)
        self.assertIn('credentials', detail_en)
        self.assertIn('practicum', detail_en)
        self.assertIn('admissions', detail_en)
        self.assertIn('snapshot', detail_en)
        self.assertIn('grants', detail_en)
        self.assertIn('faqs', detail_en)
        self.assertGreaterEqual(len(detail_en['faqs']), 4)

        # Verify detail_json_zh structure
        detail_zh = prog.get('detail_json_zh') or {}
        self.assertIn('hero', detail_zh)
        self.assertIn('stats', detail_zh)
        self.assertIn('why_choose', detail_zh)
        self.assertIn('credentials', detail_zh)
        self.assertIn('practicum', detail_zh)
        self.assertIn('admissions', detail_zh)
        self.assertIn('snapshot', detail_zh)
        self.assertIn('grants', detail_zh)
        self.assertIn('faqs', detail_zh)

    def test_04_admin_can_update_landing_page_detail_json(self):
        """Verify admin can update landing page detail JSON and it is returned on public endpoint."""
        # 1. Login as admin
        login_res = self.client.post('/api/auth/login', json={
            'email': 'admin@viccollege.com',
            'password': 'admin123'
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.get_json()['token']

        # 2. Get PSW ID and backup original detail
        psw_res = self.client.get('/api/programs/psw')
        orig_prog = psw_res.get_json()['program']
        prog_id = orig_prog['id']
        orig_detail_en = orig_prog.get('detail_json_en') or server.get_default_psw_detail_en()
        orig_detail_zh = orig_prog.get('detail_json_zh') or server.get_default_psw_detail_zh()

        try:
            # 3. Update PSW detail stats
            update_res = self.client.put(f'/api/admin/programs/{prog_id}', headers={
                'Authorization': f'Bearer {token}'
            }, json={
                'detail_json_en': {
                    'hero': {'lead': 'Updated dynamic hero lead for PSW course testing.'},
                    'stats': [
                        {'value': '23 Weeks', 'label': 'Hybrid Theory + Lab + Practicum'},
                        {'value': '$22 – $30 / hr', 'label': 'Updated GTA Starting Wage'},
                        {'value': '98% Placement', 'label': 'LTC Clinical Direct Hire'},
                        {'value': '$28,000+ Grant', 'label': 'Better Jobs Ontario'}
                    ],
                    'why_choose': {
                        'title': 'Why Choose Our PSW Diploma Program?',
                        'subtitle': 'Tested dynamic subtitle.',
                        'pillars': [
                            {'title': 'Tested Pillar 1', 'desc': 'Tested pillar desc 1.'},
                            {'title': 'Tested Pillar 2', 'desc': 'Tested pillar desc 2.'}
                        ]
                    },
                    'faqs': [
                        {'q': 'Is the PSW course accredited?', 'a': 'Yes, fully accredited under NACC.'}
                    ]
                }
            })
            self.assertEqual(update_res.status_code, 200)

            # 4. Verify on public GET /api/programs/psw
            public_res = self.client.get('/api/programs/psw')
            self.assertEqual(public_res.status_code, 200)
            updated_prog = public_res.get_json()['program']
            self.assertEqual(updated_prog['detail_json_en']['stats'][1]['value'], '$22 – $30 / hr')
            self.assertEqual(updated_prog['detail_json_en']['faqs'][0]['q'], 'Is the PSW course accredited?')
        finally:
            # Restore original detail JSON
            self.client.put(f'/api/admin/programs/{prog_id}', headers={
                'Authorization': f'Bearer {token}'
            }, json={
                'detail_json_en': server.get_default_psw_detail_en(),
                'detail_json_zh': server.get_default_psw_detail_zh()
            })

    def test_06_psw_curriculum_integrity(self):
        """Verify /api/programs/psw returns complete 15 curriculum modules and curriculum metadata."""
        res = self.client.get('/api/programs/psw')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        prog = data['program']
        
        detail_en = prog.get('detail_json_en') or {}
        self.assertIn('curriculum', detail_en)
        self.assertIn('curriculum_modules', detail_en)
        self.assertEqual(len(detail_en['curriculum_modules']), 15)
        self.assertEqual(detail_en['curriculum_modules'][0]['title'], 'PSW Foundations')
        
        detail_zh = prog.get('detail_json_zh') or {}
        self.assertIn('curriculum', detail_zh)
        self.assertIn('curriculum_modules', detail_zh)
        self.assertEqual(len(detail_zh['curriculum_modules']), 15)
        self.assertEqual(detail_zh['curriculum_modules'][0]['title'], 'PSW 基础通论')

    def test_07_admin_can_update_curriculum_modules(self):
        """Verify admin can update curriculum title, description, and modules dynamically."""
        login_res = self.client.post('/api/auth/login', json={
            'email': 'admin@viccollege.com',
            'password': 'admin123'
        })
        self.assertEqual(login_res.status_code, 200)
        token = login_res.get_json()['token']

        psw_res = self.client.get('/api/programs/psw')
        prog_id = psw_res.get_json()['program']['id']

        try:
            update_res = self.client.put(f'/api/admin/programs/{prog_id}', headers={
                'Authorization': f'Bearer {token}'
            }, json={
                'detail_json_en': {
                    'curriculum': {
                        'title': 'Custom Updated Curriculum Title',
                        'desc': 'Custom updated curriculum description text.'
                    },
                    'curriculum_modules': [
                        {'num': 1, 'title': 'Updated Module 1', 'hours': '40 Hours', 'desc': 'Custom module description 1'},
                        {'num': 2, 'title': 'Updated Module 2', 'hours': '50 Hours', 'desc': 'Custom module description 2'}
                    ]
                }
            })
            self.assertEqual(update_res.status_code, 200)

            # Check public endpoint returns updated curriculum
            public_res = self.client.get('/api/programs/psw')
            self.assertEqual(public_res.status_code, 200)
            updated_prog = public_res.get_json()['program']
            self.assertEqual(updated_prog['detail_json_en']['curriculum']['title'], 'Custom Updated Curriculum Title')
            self.assertEqual(len(updated_prog['detail_json_en']['curriculum_modules']), 2)
            self.assertEqual(updated_prog['detail_json_en']['curriculum_modules'][0]['title'], 'Updated Module 1')
        finally:
            # Restore default details
            self.client.put(f'/api/admin/programs/{prog_id}', headers={
                'Authorization': f'Bearer {token}'
            }, json={
                'detail_json_en': server.get_default_psw_detail_en(),
                'detail_json_zh': server.get_default_psw_detail_zh()
            })

if __name__ == '__main__':
    unittest.main()


