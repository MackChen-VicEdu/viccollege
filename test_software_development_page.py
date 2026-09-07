import unittest
import json
from server import app, get_db

class TestSoftwareDevelopmentPage(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_software_dev_page_serves_200_and_has_dom_structure(self):
        """Verify software-development.html serves 200 on all aliases and has expected DOM structure."""
        paths = [
            '/software-development',
            '/software-development/',
            '/software-development.html',
            '/fullstack',
            '/fullstack.html',
            '/full-stack-web-development-ai',
            '/software-development-course'
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
            self.assertIn('tech_page_title', html)
            self.assertIn('id="tech-hero-badge"', html)
            self.assertIn('id="tech-hero-title"', html)
            self.assertIn('id="tech-hero-lead"', html)
            self.assertIn('id="tech-curriculum-list"', html)
            self.assertIn('id="tech-stat-1-val"', html)
            self.assertIn('id="tech-stat-4-val"', html)
            self.assertIn('id="tech-pillars-grid"', html)
            self.assertIn('id="tech-credentials-grid"', html)
            self.assertIn('id="tech-practicum"', html)
            self.assertIn('id="tech-admissions-list"', html)
            self.assertIn('id="tech-faq-list"', html)
            self.assertIn('id="tech-consultation-form"', html)

            # Key domain terms
            self.assertIn('React 19', html)
            self.assertIn('Spring Boot 3', html)
            self.assertIn('TypeScript', html)
            self.assertIn('Next.js', html)
            self.assertIn('AWS', html)
            self.assertIn('Ontario Career Colleges Act, 2005', html)

    def test_software_dev_api_endpoints_and_aliases(self):
        """Verify /api/programs/tech and all alias routes return full detail and 10 modules."""
        aliases = [
            'tech',
            'fullstack',
            'software-development',
            'full-stack-web-development-ai',
            'software-development-course',
            'software-development-program',
            'full-stack'
        ]
        for slug in aliases:
            res = self.client.get(f'/api/programs/{slug}')
            self.assertEqual(res.status_code, 200, f"API failed for alias {slug}")
            data = json.loads(res.data.decode('utf-8'))
            self.assertTrue(data.get('success'))
            program = data.get('program')
            self.assertIsNotNone(program)
            self.assertEqual(program.get('slug'), 'tech')

            # Check detail_json_en
            detail_en = program.get('detail_json_en')
            self.assertIsInstance(detail_en, dict)
            self.assertIn('hero', detail_en)
            self.assertIn('curriculum_modules', detail_en)
            modules = detail_en['curriculum_modules']
            self.assertEqual(len(modules), 10, f"Expected 10 modules in EN detail for {slug}")
            self.assertEqual(modules[0]['num'], 1)
            self.assertIn('Computer Science Fundamentals', modules[0]['title'])
            self.assertIn('React 19', modules[2]['title'])
            self.assertIn('Spring Boot', modules[5]['title'])
            self.assertIn('Generative AI', modules[7]['title'])
            self.assertIn('Cloud Infrastructure', modules[8]['title'])

            # Check detail_json_zh
            detail_zh = program.get('detail_json_zh')
            self.assertIsInstance(detail_zh, dict)
            self.assertIn('curriculum_modules', detail_zh)
            self.assertEqual(len(detail_zh['curriculum_modules']), 10, f"Expected 10 modules in ZH detail for {slug}")

    def test_links_from_all_landing_and_home_pages(self):
        """Verify index.html, PSW, Accounting, ECA, Acupuncture, and Electrician pages link to software-development.html."""
        pages = [
            ('/', 'index.html'),
            ('/personal-support-worker-online-psw-course.html', 'psw page'),
            ('/computerized-accounting.html', 'accounting page'),
            ('/early-childcare-assistant-eca.html', 'eca page'),
            ('/acupuncture-program.html', 'acupuncture page'),
            ('/electrician.html', 'electrician page'),
        ]
        for path, desc in pages:
            res = self.client.get(path)
            html = res.data.decode('utf-8')
            self.assertIn('software-development.html', html, f"{desc} ({path}) should link to software-development.html")

        # Specific check for index.html card button
        res_home = self.client.get('/')
        html_home = res_home.data.decode('utf-8')
        self.assertIn('<a href="software-development.html" class="btn-learn-more">', html_home)

    def test_consultation_form_submission_for_software_dev(self):
        """Verify lead consultation submission records tech program in DB."""
        payload = {
            'name': 'Sarah Connor',
            'email': 'sarah.connor@example.com',
            'phone': '416-555-8899',
            'program': 'Full Stack Web with AI Mini-Credential',
            'interested_in_grant': 1,
            'source_page': 'software-development'
        }
        res = self.client.post('/api/consultations', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data.get('success'))
        self.assertIn('id', data)

    def test_dynamic_app_js_routes_software_dev_to_landing_page(self):
        """Verify js/app.js contains dynamic card and dropdown mappings for software-development.html."""
        res = self.client.get('/js/app.js')
        self.assertEqual(res.status_code, 200)
        js = res.data.decode('utf-8')
        self.assertIn("prog.slug === 'tech'", js)
        self.assertIn('<a href="software-development.html" class="btn-learn-more">', js)
        self.assertIn("p.slug === 'tech' || p.slug === 'fullstack' || p.slug === 'software-development'", js)

if __name__ == '__main__':
    unittest.main()
