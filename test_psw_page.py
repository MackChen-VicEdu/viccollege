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
        self.assertIn('id="psw-stat-duration"', html)
        self.assertIn('id="psw-curriculum-list"', html)
        self.assertIn('id="psw-side-credential"', html)
        self.assertIn('id="psw-side-duration"', html)
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
        """Verify /api/programs/psw returns full bilingual data for dynamic hydration."""
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

    def test_04_consultation_submission_from_psw_page(self):
        """Verify consultation form from PSW page submits cleanly to /api/consultations."""
        res = self.client.post('/api/consultations', json={
            'name': 'Dynamic Test Lead',
            'email': 'dynamic.lead@example.com',
            'phone': '416-555-0199',
            'program': 'psw',
            'interested_in_grant': 1,
            'source_page': 'personal-support-worker-online-psw-course'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()
