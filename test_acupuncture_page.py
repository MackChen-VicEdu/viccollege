import unittest
import json
from server import app, get_db

class TestAcupuncturePage(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_acupuncture_page_serves_200_and_has_dom_structure(self):
        """Verify acupuncture-program.html serves 200 and has dynamic IDs."""
        for path in ['/acupuncture-program.html', '/acupuncture-program', '/acupuncture-program/', '/acupuncture', '/acupuncture.html', '/acupuncture-course']:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200)
            html = res.data.decode('utf-8')
            
            # Header check (clean vic-main-header, no legacy top-bar)
            self.assertIn('class="vic-main-header"', html)
            self.assertNotIn('class="top-bar-clean"', html)
            self.assertNotIn('class="header-top-bar"', html)
            
            # Dynamic and i18n DOM elements
            self.assertIn('acu_page_title', html)
            self.assertIn('id="acu-hero-badge"', html)
            self.assertIn('id="acu-hero-title"', html)
            self.assertIn('id="acu-hero-lead"', html)
            self.assertIn('id="acu-curriculum-list"', html)
            self.assertIn('id="acu-stat-1-val"', html)
            self.assertIn('id="acu-stat-4-val"', html)
            self.assertIn('id="acu-pillars-grid"', html)
            self.assertIn('id="acu-credentials-grid"', html)
            self.assertIn('id="schedule"', html)
            self.assertIn('id="acu-admissions-list"', html)
            self.assertIn('id="acu-faq-list"', html)
            self.assertIn('id="acu-consultation-form"', html)
            
            # Key domain terms
            self.assertIn('2250 Hours', html)
            self.assertIn('TCM Wisdom', html)
            self.assertIn('Ontario Career Colleges Act, 2005', html)
            self.assertIn('14 Meridian Channels', html)

    def test_acupuncture_api_endpoints_and_aliases(self):
        """Verify /api/programs/acupuncture and aliases return full detail and 10 modules."""
        for slug in ['acupuncture', 'acupuncture-program', 'acupuncture-course', 'tcm-acupuncture']:
            res = self.client.get(f'/api/programs/{slug}')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data.decode('utf-8'))
            self.assertTrue(data.get('success'))
            program = data.get('program')
            self.assertIsNotNone(program)
            self.assertEqual(program.get('slug'), 'acupuncture')
            
            # Check detail_json_en
            detail_en = program.get('detail_json_en')
            self.assertIsInstance(detail_en, dict)
            self.assertIn('hero', detail_en)
            self.assertIn('curriculum_modules', detail_en)
            modules = detail_en['curriculum_modules']
            self.assertEqual(len(modules), 10)
            self.assertEqual(modules[0]['num'], 1)
            self.assertIn('Foundation', modules[0]['title'])
            self.assertIn('Meridian', modules[1]['title'])
            self.assertEqual(detail_en.get('total_hours'), '2250 Hours')

            # Check detail_json_zh
            detail_zh = program.get('detail_json_zh')
            self.assertIsInstance(detail_zh, dict)
            self.assertIn('curriculum_modules', detail_zh)
            self.assertEqual(len(detail_zh['curriculum_modules']), 10)

    def test_links_from_index_psw_accounting_and_eca_pages(self):
        """Verify index.html, PSW, Accounting, and ECA pages contain links to acupuncture-program.html."""
        pages = [
            ('/', 'index.html'),
            ('/personal-support-worker-online-psw-course.html', 'psw page'),
            ('/computerized-accounting.html', 'accounting page'),
            ('/early-childcare-assistant-eca.html', 'eca page'),
        ]
        for path, desc in pages:
            res = self.client.get(path)
            html = res.data.decode('utf-8')
            self.assertIn('acupuncture-program.html', html, f"{desc} should link to acupuncture-program.html")

        # Specific check for index.html card button
        res_home = self.client.get('/')
        html_home = res_home.data.decode('utf-8')
        self.assertIn('<a href="acupuncture-program.html" class="btn-learn-more">', html_home)

    def test_consultation_form_submission_for_acupuncture(self):
        """Verify lead consultation submission records acupuncture program in DB."""
        payload = {
            'name': 'Alex Wong',
            'email': 'alex.wong@example.com',
            'phone': '416-555-9876',
            'program': 'acupuncture',
            'interested_in_grant': 0,
            'source_page': 'acupuncture-program'
        }
        res = self.client.post('/api/consultations', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data.get('success'))
        self.assertIn('id', data)

if __name__ == '__main__':
    unittest.main()
