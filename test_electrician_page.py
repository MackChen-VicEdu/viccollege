import unittest
import json
from server import app, get_db

class TestElectricianPage(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_electrician_page_serves_200_and_has_dom_structure(self):
        """Verify electrician.html serves 200 on all aliases and has expected DOM structure."""
        paths = [
            '/electrician',
            '/electrician/',
            '/electrician.html',
            '/electrician-309a-442a',
            '/electrician-course',
            '/electrician-training'
        ]
        for path in paths:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Failed for path {path}")
            html = res.data.decode('utf-8')

            # Header check (clean standard vic-main-header, no legacy top-bar)
            self.assertIn('class="vic-main-header"', html)
            self.assertNotIn('class="top-bar-clean"', html)
            self.assertNotIn('class="header-top-bar"', html)

            # Dynamic and i18n DOM elements
            self.assertIn('elec_page_title', html)
            self.assertIn('id="elec-hero-badge"', html)
            self.assertIn('id="elec-hero-title"', html)
            self.assertIn('id="elec-hero-lead"', html)
            self.assertIn('id="elec-curriculum-list"', html)
            self.assertIn('id="elec-stat-1-val"', html)
            self.assertIn('id="elec-stat-4-val"', html)
            self.assertIn('id="elec-pillars-grid"', html)
            self.assertIn('id="elec-credentials-grid"', html)
            self.assertIn('id="elec-practicum"', html)
            self.assertIn('id="elec-admissions-list"', html)
            self.assertIn('id="elec-faq-list"', html)
            self.assertIn('id="elec-consultation-form"', html)

            # Key domain terms
            self.assertIn('309A', html)
            self.assertIn('442A', html)
            self.assertIn('Canadian Electrical Code (CEC)', html)
            self.assertIn('Ontario Career Colleges Act, 2005', html)

    def test_electrician_api_endpoints_and_aliases(self):
        """Verify /api/programs/electrician and all alias routes return full detail and 10 modules."""
        aliases = [
            'electrician',
            'electrician-309a',
            'electrician-442a',
            'electrician-course',
            'electrician-training',
            'electrician-program',
            '309a-electrician',
            '442a-electrician'
        ]
        for slug in aliases:
            res = self.client.get(f'/api/programs/{slug}')
            self.assertEqual(res.status_code, 200, f"API failed for alias {slug}")
            data = json.loads(res.data.decode('utf-8'))
            self.assertTrue(data.get('success'))
            program = data.get('program')
            self.assertIsNotNone(program)
            self.assertEqual(program.get('slug'), 'electrician')

            # Check detail_json_en
            detail_en = program.get('detail_json_en')
            self.assertIsInstance(detail_en, dict)
            self.assertIn('hero', detail_en)
            self.assertIn('curriculum_modules', detail_en)
            modules = detail_en['curriculum_modules']
            self.assertEqual(len(modules), 10, f"Expected 10 modules in EN detail for {slug}")
            self.assertEqual(modules[0]['num'], 1)
            self.assertIn('Canadian Electrical Code', modules[0]['title'])
            self.assertIn('Residential Wiring', modules[3]['title'])
            self.assertIn('Conduit Bending', modules[7]['title'])

            # Check detail_json_zh
            detail_zh = program.get('detail_json_zh')
            self.assertIsInstance(detail_zh, dict)
            self.assertIn('curriculum_modules', detail_zh)
            self.assertEqual(len(detail_zh['curriculum_modules']), 10, f"Expected 10 modules in ZH detail for {slug}")

    def test_links_from_all_landing_and_home_pages(self):
        """Verify index.html, PSW, Accounting, ECA, and Acupuncture pages link to electrician.html."""
        pages = [
            ('/', 'index.html'),
            ('/personal-support-worker-online-psw-course.html', 'psw page'),
            ('/computerized-accounting.html', 'accounting page'),
            ('/early-childcare-assistant-eca.html', 'eca page'),
            ('/acupuncture-program.html', 'acupuncture page'),
        ]
        for path, desc in pages:
            res = self.client.get(path)
            html = res.data.decode('utf-8')
            self.assertIn('electrician.html', html, f"{desc} ({path}) should link to electrician.html")

        # Specific check for index.html card button
        res_home = self.client.get('/')
        html_home = res_home.data.decode('utf-8')
        self.assertIn('<a href="electrician.html" class="btn-learn-more">', html_home)

    def test_consultation_form_submission_for_electrician(self):
        """Verify lead consultation submission records electrician program in DB."""
        payload = {
            'name': 'Jason Miller',
            'email': 'jason.miller@example.com',
            'phone': '416-555-4321',
            'program': 'Electrician (309A / 442A)',
            'interested_in_grant': 1,
            'source_page': 'electrician'
        }
        res = self.client.post('/api/consultations', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data.get('success'))
        self.assertIn('id', data)

    def test_dynamic_app_js_routes_electrician_to_landing_page(self):
        """Verify js/app.js contains dynamic card and dropdown mappings for electrician.html."""
        res = self.client.get('/js/app.js')
        self.assertEqual(res.status_code, 200)
        js = res.data.decode('utf-8')
        self.assertIn("prog.slug === 'electrician'", js)
        self.assertIn('<a href="electrician.html" class="btn-learn-more">', js)
        self.assertIn("p.slug === 'electrician'\n                ? 'electrician.html'", js)

if __name__ == '__main__':
    unittest.main()
