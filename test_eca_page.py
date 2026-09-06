import unittest
import json
from server import app, get_db

class TestEcaPage(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_eca_page_serves_200_and_has_dom_structure(self):
        """Verify early-childcare-assistant-eca.html serves 200 and has dynamic IDs."""
        for path in ['/early-childcare-assistant-eca.html', '/early-childcare-assistant-eca', '/early-childcare-assistant-eca/', '/early-childcare-assistant']:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200)
            html = res.data.decode('utf-8')
            self.assertIn('eca_page_title', html)
            self.assertIn('id="eca-hero-badge"', html)
            self.assertIn('id="eca-hero-title"', html)
            self.assertIn('id="eca-hero-lead"', html)
            self.assertIn('id="eca-curriculum-list"', html)
            self.assertIn('id="eca-stat-1-val"', html)
            self.assertIn('id="eca-stat-4-val"', html)
            self.assertIn('id="eca-pillars-grid"', html)
            self.assertIn('id="eca-credentials-grid"', html)
            self.assertIn('id="eca-admissions-list"', html)
            self.assertIn('id="eca-faq-list"', html)
            self.assertIn('id="eca-consultation-form"', html)
            self.assertIn('Early Childcare Assistant', html)
            self.assertIn('500+ Hours', html)
            self.assertIn('Licensed Ontario Daycares', html)

    def test_eca_api_endpoints_and_aliases(self):
        """Verify /api/programs/eca and aliases return full detail and 10 modules."""
        for slug in ['eca', 'early-childcare-assistant', 'early-childcare-assistant-eca', 'eca-course']:
            res = self.client.get(f'/api/programs/{slug}')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data.decode('utf-8'))
            self.assertTrue(data.get('success'))
            program = data.get('program')
            self.assertIsNotNone(program)
            self.assertEqual(program.get('slug'), 'eca')
            
            # Check detail_json_en
            detail_en = program.get('detail_json_en')
            self.assertIsInstance(detail_en, dict)
            self.assertIn('hero', detail_en)
            self.assertIn('curriculum_modules', detail_en)
            modules = detail_en['curriculum_modules']
            self.assertEqual(len(modules), 10)
            self.assertEqual(modules[0]['num'], 1)
            self.assertIn('Early Childhood Education', modules[0]['title'])
            self.assertIn('Infancy to Toddlerhood', modules[1]['title'])
            self.assertIn('Practicum', modules[9]['title'])

    def test_links_from_index_psw_and_accounting_pages(self):
        """Verify index.html, PSW page, and Accounting page contain links to early-childcare-assistant-eca.html."""
        for path in ['/', '/personal-support-worker-online-psw-course.html', '/computerized-accounting.html']:
            res = self.client.get(path)
            html = res.data.decode('utf-8')
            self.assertIn('early-childcare-assistant-eca.html', html)

    def test_consultation_form_submission_for_eca(self):
        """Verify consultation booking submits successfully for early childcare assistant."""
        lead_data = {
            'name': 'Sarah Wang',
            'email': 'sarah.wang.eca.test@example.com',
            'phone': '416-555-9876',
            'program': 'Early Childcare Assistant (ECA)',
            'interested_in_grant': 1,
            'source_page': 'early-childcare-assistant-eca'
        }
        res = self.client.post('/api/consultations',
                               data=json.dumps(lead_data),
                               content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data.get('success'))
        self.assertIn('id', data)

if __name__ == '__main__':
    unittest.main()
