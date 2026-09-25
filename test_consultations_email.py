import unittest
import json
from unittest.mock import patch, MagicMock
from server import (
    app, init_database, get_db_connection, build_admin_lead_email, build_student_welcome_email,
    get_smtp_config, send_smtp_email
)

class TestConsultationsAndEmail(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_database()

    def setUp(self):
        self.client = app.test_client()
        app.testing = True

        # Clean up existing test consultations if any and reset settings
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM consultations WHERE email LIKE '%@testdomain.com'")
        cursor.execute("DELETE FROM settings WHERE key IN ('student_email_subject', 'student_email_body', 'admin_email_subject')")
        conn.commit()
        conn.close()

        # Obtain valid admin token
        login_res = self.client.post("/api/auth/login", json={
            "email": "admin@viccollege.com",
            "password": "Admin@123456"
        })
        login_data = login_res.get_json() or {}
        self.admin_token = login_data.get('token', '')
        self.auth_headers = {"Authorization": f"Bearer {self.admin_token}"}

    def tearDown(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM consultations WHERE email LIKE '%@testdomain.com'")
        cursor.execute("DELETE FROM settings WHERE key IN ('student_email_subject', 'student_email_body', 'admin_email_subject')")
        conn.commit()
        conn.close()

    def test_post_free_class_lead(self):
        """Test submitting a Free Class lead from the homepage form."""
        payload = {
            "name": "Alex FreeClass",
            "email": "alex.free@testdomain.com",
            "phone": "416-555-0199",
            "interest": "free_class",
            "notes": "Interested in Weekend Free Trial Class"
        }
        response = self.client.post(
            '/api/consultations',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data.get("success"))
        self.assertIn("id", data)

        # Check in DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, email, phone, interest, status FROM consultations WHERE id = ?", (data["id"],))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "Alex FreeClass")
        self.assertEqual(row["email"], "alex.free@testdomain.com")
        self.assertEqual(row["phone"], "416-555-0199")
        self.assertEqual(row["interest"], "free_class")
        self.assertEqual(row["status"], "new")

    def test_post_consultation_lead(self):
        """Test submitting a Consultation lead with program and campus."""
        payload = {
            "name": "Maria Student",
            "email": "maria.student@testdomain.com",
            "phone": "647-555-0123",
            "program": "Personal Support Worker (PSW)",
            "campus": "North York",
            "interest": "Personal Support Worker (PSW)",
            "notes": "Looking to start next month."
        }
        response = self.client.post(
            '/api/consultations',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data.get("success"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM consultations WHERE id = ?", (data["id"],))
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "Maria Student")
        self.assertEqual(row["program"], "Personal Support Worker (PSW)")
        self.assertEqual(row["campus"], "North York")

    def test_post_consultation_validation(self):
        """Test validation fails if required fields are missing."""
        # Missing name
        response = self.client.post(
            '/api/consultations',
            data=json.dumps({"email": "test@testdomain.com"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data.get("success", False))

        # Missing both email and phone
        response = self.client.post(
            '/api/consultations',
            data=json.dumps({"name": "No Contact Info"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data.get("success", False))

    def test_email_builders(self):
        """Test the email formatting utilities for admin and student."""
        lead = {
            "name": "Jane Doe",
            "email": "jane@testdomain.com",
            "phone": "416-000-1111",
            "program": "Acupuncture",
            "campus": "Markham",
            "interest": "free_class",
            "notes": "Please contact morning only."
        }
        # Admin lead email
        html_body = build_admin_lead_email(lead)
        self.assertIn("Jane Doe", html_body)
        self.assertIn("jane@testdomain.com", html_body)
        self.assertIn("416-000-1111", html_body)
        self.assertIn("Acupuncture", html_body)
        self.assertIn("<table", html_body)

        # Student welcome email
        stu_html = build_student_welcome_email(lead)
        self.assertIn("Victoria International College", stu_html)
        self.assertIn("Jane Doe", stu_html)
        self.assertIn("Acupuncture", stu_html)
        self.assertIn("info@viccollege.com", stu_html)

    def test_admin_consultations_crud(self):
        """Test admin list, filter, status update, and delete for consultations."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO consultations (name, email, phone, interest, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("Lead One", "one@testdomain.com", "111-111", "free_class", "new", "2026-09-19T00:00:00")
        )
        lead_id_1 = cursor.lastrowid
        cursor.execute(
            "INSERT INTO consultations (name, email, phone, interest, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("Lead Two", "two@testdomain.com", "222-222", "Accounting", "contacted", "2026-09-19T00:00:00")
        )
        lead_id_2 = cursor.lastrowid
        conn.commit()
        conn.close()

        # GET /api/admin/consultations
        res = self.client.get('/api/admin/consultations', headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        leads = res.get_json().get("leads", [])
        lead_ids = [l["id"] for l in leads]
        self.assertIn(lead_id_1, lead_ids)
        self.assertIn(lead_id_2, lead_ids)

        # Filter by status = 'new'
        res_filtered = self.client.get('/api/admin/consultations?status=new', headers=self.auth_headers)
        self.assertEqual(res_filtered.status_code, 200)
        leads_new = res_filtered.get_json().get("leads", [])
        self.assertTrue(all(l["status"] == "new" for l in leads_new))

        # Search by query
        res_search = self.client.get('/api/admin/consultations?search=one@testdomain.com', headers=self.auth_headers)
        self.assertEqual(res_search.status_code, 200)
        leads_search = res_search.get_json().get("leads", [])
        self.assertEqual(len(leads_search), 1)
        self.assertEqual(leads_search[0]["id"], lead_id_1)

        # PATCH /api/admin/consultations/<id> status update
        res_patch = self.client.patch(
            f'/api/admin/consultations/{lead_id_1}',
            data=json.dumps({"status": "enrolled", "notes": "Registered for May intake"}),
            content_type='application/json',
            headers=self.auth_headers
        )
        self.assertEqual(res_patch.status_code, 200)
        data_patch = res_patch.get_json()
        self.assertTrue(data_patch.get("success"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, notes FROM consultations WHERE id = ?", (lead_id_1,))
        updated_lead = cursor.fetchone()
        conn.close()
        self.assertEqual(updated_lead["status"], "enrolled")
        self.assertIn("Registered for May intake", updated_lead["notes"])

        # DELETE /api/admin/consultations/<id>
        res_del = self.client.delete(f'/api/admin/consultations/{lead_id_1}', headers=self.auth_headers)
        self.assertEqual(res_del.status_code, 200)
        self.assertTrue(res_del.get_json().get("success"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM consultations WHERE id = ?", (lead_id_1,))
        deleted_row = cursor.fetchone()
        conn.close()
        self.assertIsNone(deleted_row)

    def test_smtp_settings_and_test_email(self):
        """Test SMTP settings management and test email diagnostic endpoint."""
        smtp_payload = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": "587",
            "smtp_user": "admissions@testdomain.com",
            "smtp_pass": "SecretPass123!",
            "smtp_sender_name": "Victoria College Admissions",
            "smtp_recipient": "leads@testdomain.com",
            "smtp_tls": "tls"
        }
        res_save = self.client.post(
            '/api/admin/settings',
            data=json.dumps(smtp_payload),
            content_type='application/json',
            headers=self.auth_headers
        )
        self.assertEqual(res_save.status_code, 200)
        self.assertTrue(res_save.get_json().get("success"))

        # Verify GET /api/admin/settings masks password
        res_get = self.client.get('/api/admin/settings', headers=self.auth_headers)
        self.assertEqual(res_get.status_code, 200)
        settings = res_get.get_json().get("settings", {})
        self.assertEqual(settings.get("smtp_host"), "smtp.gmail.com")
        self.assertEqual(settings.get("smtp_user"), "admissions@testdomain.com")
        self.assertEqual(settings.get("smtp_recipient"), "leads@testdomain.com")
        self.assertEqual(settings.get("smtp_pass"), "••••••••••••")

        # Test sending test email (simulated / mock)
        with patch("smtplib.SMTP") as mock_smtp:
            mock_server_inst = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server_inst

            res_test_email = self.client.post(
                '/api/admin/settings/test-email',
                data=json.dumps({"target_email": "tester@testdomain.com"}),
                content_type='application/json',
                headers=self.auth_headers
            )
            self.assertEqual(res_test_email.status_code, 200)
            data_email = res_test_email.get_json()
            self.assertTrue(data_email.get("success"))
            self.assertIn("tester@testdomain.com", data_email.get("message"))

    def test_admin_send_lead_email(self):
        """Test admin sending welcome email to a student lead."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO consultations (name, email, phone, program, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("Email Test Student", "teststudent@testdomain.com", "416-555-9999", "PSW", "new", "2026-09-19T00:00:00")
        )
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()

        with patch("smtplib.SMTP") as mock_smtp:
            mock_server_inst = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server_inst

            res = self.client.post(
                f'/api/admin/consultations/{lead_id}/send-email',
                data=json.dumps({"subject": "Custom Class Welcome", "message": "Your class starts Monday!"}),
                content_type='application/json',
                headers=self.auth_headers
            )
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertTrue(data.get("success"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM consultations WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        conn.close()
        self.assertEqual(row["status"], "contacted")

    def test_editable_templates_and_lead_email_preview(self):
        """Test saving custom email templates, previewing per-lead interpolated content, and custom send."""
        # 1. Save custom template
        custom_subj = "Welcome to Vic College {name} - {program}!"
        custom_body = "Hello {name},\nWe are thrilled you registered for {program} at {campus}.\nCall us at {admissions_phone}."
        custom_admin_subj = "[HOT LEAD] {name} applied for {program}"

        save_res = self.client.post(
            '/api/admin/settings',
            data=json.dumps({
                "student_email_subject": custom_subj,
                "student_email_body": custom_body,
                "admin_email_subject": custom_admin_subj
            }),
            content_type='application/json',
            headers=self.auth_headers
        )
        self.assertEqual(save_res.status_code, 200)

        # 2. Insert test lead
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO consultations (name, email, phone, program, campus, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("Evelyn Harper", "evelyn@testdomain.com", "416-888-9999", "Acupuncture", "Markham", "new", "2026-09-19T00:00:00")
        )
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # 3. Test GET email preview endpoint
        preview_res = self.client.get(
            f'/api/admin/consultations/{lead_id}/email-preview',
            headers=self.auth_headers
        )
        self.assertEqual(preview_res.status_code, 200)
        p_data = preview_res.get_json()
        self.assertTrue(p_data.get("success"))
        self.assertEqual(p_data.get("subject"), "Welcome to Vic College Evelyn Harper - Acupuncture!")
        self.assertIn("Hello Evelyn Harper,", p_data.get("message_body"))
        self.assertIn("Acupuncture", p_data.get("message_body"))
        self.assertIn("Markham", p_data.get("message_body"))
        self.assertIn("html_preview", p_data)

        # 4. Test POST custom email override
        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            send_res = self.client.post(
                f'/api/admin/consultations/{lead_id}/send-email',
                data=json.dumps({
                    "subject": "Special Fast-Track Invitation for Evelyn",
                    "message": "Hi Evelyn,\nHere is your custom class schedule for Saturday."
                }),
                content_type='application/json',
                headers=self.auth_headers
            )
            self.assertEqual(send_res.status_code, 200)
            s_data = send_res.get_json()
            self.assertTrue(s_data.get("success"))

if __name__ == '__main__':
    unittest.main()

