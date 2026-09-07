import unittest
from server import app

class TestPolicyPages(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_privacy_policy_page(self):
        """Verify privacy-policy.html serves 200 on all aliases and contains required sections."""
        for path in ['/privacy-policy', '/privacy-policy/', '/privacy-policy.html']:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Failed for {path}")
            html = res.data.decode('utf-8')
            self.assertIn('policy_privacy_title', html)
            self.assertIn('Information Collection and Use', html)
            self.assertIn('Cookies', html)
            self.assertIn('Log Files', html)
            self.assertIn('Protection of Children', html)
            self.assertIn('416-665-6668', html)
            self.assertIn('info@viccollege.com', html)

    def test_kpi_audit_requirements_page(self):
        """Verify kpi-audit-requirements.html serves 200 on all aliases and contains required content."""
        for path in ['/kpi-audit-requirements', '/KPI-audit-requirements', '/kpi-audit-requirements.html', '/KPI-audit-requirements.html']:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Failed for {path}")
            html = res.data.decode('utf-8')
            self.assertIn('policy_kpi_title', html)
            self.assertIn('Key Performance Indicator', html)
            self.assertIn('Graduate Employment Rate', html)
            self.assertIn('PCC ID: 102208', html)
            self.assertIn('https://www.tcu.gov.on.ca/pepg/audiences/pcc/2023-pcc-kpi/data/?pccid=102208', html)

    def test_sexual_violence_policy_page(self):
        """Verify sexual-violence-policy.html serves 200 on all aliases and contains required content."""
        for path in ['/sexual-violence-policy', '/sexual-violence-policy/', '/sexual-violence-policy.html']:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Failed for {path}")
            html = res.data.decode('utf-8')
            self.assertIn('policy_sexual_title', html)
            self.assertIn('Statement from the Director', html)
            self.assertIn('Maria Sun', html)
            self.assertIn('Tiffany Tao', html)
            self.assertIn('Aria Ye', html)
            self.assertIn('1-866-863-0511', html) # Assaulted Women's Helpline
            self.assertIn('Fem\'aide', html)
            self.assertIn('Dispelling Myths and Misconceptions', html)

    def test_students_complaint_procedure_page(self):
        """Verify students-complaint-procedure.html serves 200 on all aliases and contains required 4 steps."""
        for path in ['/students-complaint-procedure', '/students-complaint-procedure.html', '/student-complaint-procedure', '/student-complaint-procedure.html']:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Failed for {path}")
            html = res.data.decode('utf-8')
            self.assertIn('policy_complaint_title', html)
            self.assertIn('Student Complaint Resolution Procedure', html)
            self.assertIn('Maria Sun', html)
            self.assertIn('Section 36 of O. Reg. 415/06', html)
            self.assertIn('PARIS', html)
            self.assertIn('https://www.pcc.tcu.gov.on.ca/PARISExtWeb/public/login.xhtml', html)
            self.assertIn('Step 1', html)
            self.assertIn('Step 2', html)
            self.assertIn('Step 3', html)
            self.assertIn('Step 4', html)

    def test_academic_accommodation_page(self):
        """Verify academic accommodation policy serves 200 on all aliases and contains required content."""
        for path in [
            '/academic-accommodation-policy-and-procedure-for-students-with-disabilities',
            '/academic-accommodation-policy-and-procedure-for-students-with-disabilities.html',
            '/academic-accommodation-policy',
            '/academic-accommodation'
        ]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200, f"Failed for {path}")
            html = res.data.decode('utf-8')
            self.assertIn('policy_disability_title', html)
            self.assertIn('Academic Accommodation Policy &amp; Procedure for Students with Disabilities', html)
            self.assertIn('Accessibility for Ontarians with Disabilities Act', html)
            self.assertIn('Ontario Human Rights Code', html)
            self.assertIn('Letter of Accommodation', html)
            self.assertIn('Undue Hardship', html)

    def test_all_pages_contain_policy_footer_links(self):
        """Verify all site pages include links to the 5 policies in their footers."""
        pages = [
            '/',
            '/personal-support-worker-online-psw-course.html',
            '/computerized-accounting.html',
            '/early-childcare-assistant-eca.html',
            '/acupuncture-program.html',
            '/electrician.html',
            '/software-development.html',
            '/privacy-policy.html',
            '/kpi-audit-requirements.html',
            '/sexual-violence-policy.html',
            '/students-complaint-procedure.html',
            '/academic-accommodation-policy-and-procedure-for-students-with-disabilities.html'
        ]

        expected_links = [
            'privacy-policy.html',
            'kpi-audit-requirements.html',
            'sexual-violence-policy.html',
            'students-complaint-procedure.html',
            'academic-accommodation-policy-and-procedure-for-students-with-disabilities.html'
        ]

        for p in pages:
            res = self.client.get(p)
            self.assertEqual(res.status_code, 200, f"Failed for page {p}")
            html = res.data.decode('utf-8')
            for link in expected_links:
                self.assertIn(link, html, f"Page {p} missing footer link {link}")

if __name__ == '__main__':
    unittest.main()
