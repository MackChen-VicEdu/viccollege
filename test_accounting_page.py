import unittest
import json
from server import app, get_db

class TestAccountingPage(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_accounting_page_serves_200_and_has_dom_structure(self):
        """Verify computerized-accounting.html serves 200 and has dynamic IDs."""
        for path in ['/computerized-accounting.html', '/computerized-accounting', '/computerized-accounting/']:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200)
            html = res.data.decode('utf-8')
            self.assertIn('acc_page_title', html)
            self.assertIn('id="acc-hero-badge"', html)
            self.assertIn('id="acc-hero-title"', html)
            self.assertIn('id="acc-hero-lead"', html)
            self.assertIn('id="acc-curriculum-list"', html)
            self.assertIn('id="acc-stat-1-val"', html)
            self.assertIn('id="acc-stat-4-val"', html)
            self.assertIn('id="acc-pillars-grid"', html)
            self.assertIn('id="acc-credentials-grid"', html)
            self.assertIn('id="acc-admissions-list"', html)
            self.assertIn('id="acc-faq-list"', html)
            self.assertIn('id="acc-consultation-form"', html)
            self.assertIn('QuickBooks', html)
            self.assertIn('Sage 50', html)
            self.assertIn('ACCPAC', html)
            self.assertIn('Taxprep', html)

    def test_accounting_api_endpoints_and_aliases(self):
        """Verify /api/programs/accounting and /api/programs/computerized-accounting return full detail and 10 modules."""
        for slug in ['accounting', 'computerized-accounting', 'accounting-tax-payroll']:
            res = self.client.get(f'/api/programs/{slug}')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data.decode('utf-8'))
            self.assertTrue(data.get('success'))
            program = data.get('program')
            self.assertIsNotNone(program)
            self.assertEqual(program.get('slug'), 'accounting')
            
            # Check detail_json_en
            detail_en = program.get('detail_json_en')
            self.assertIsInstance(detail_en, dict)
            self.assertIn('hero', detail_en)
            self.assertIn('curriculum_modules', detail_en)
            modules = detail_en['curriculum_modules']
            self.assertEqual(len(modules), 10)
            self.assertEqual(modules[0]['num'], 1)
            self.assertIn('QuickBooks', modules[1]['title'])
            self.assertIn('Sage 50', modules[2]['title'])

    def test_links_from_index_and_psw_pages(self):
        """Verify index.html and PSW page contain links to computerized-accounting.html."""
        res = self.client.get('/')
        html = res.data.decode('utf-8')
        self.assertIn('href="computerized-accounting.html"', html)
        self.assertIn('<a href="computerized-accounting.html" data-i18n="prog_acc_title">Accounting, Tax and Payroll</a>', html)
        self.assertIn('<a href="computerized-accounting.html" class="btn-learn-more">', html)

        res_psw = self.client.get('/personal-support-worker-online-psw-course.html')
        html_psw = res_psw.data.decode('utf-8')
        self.assertIn('href="computerized-accounting.html"', html_psw)

    def test_consultation_form_submission_for_accounting(self):
        """Verify lead consultation submission records accounting program in DB."""
        payload = {
            'name': 'David Zhang',
            'email': 'david.zhang@example.com',
            'phone': '416-665-6668',
            'program': 'accounting',
            'interested_in_grant': 1,
            'source_page': 'computerized-accounting'
        }
        res = self.client.post('/api/consultations', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data.get('success'))
        self.assertIn('id', data)

if __name__ == '__main__':
    unittest.main()
