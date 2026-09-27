"""
Unit & Integration Tests for Admin Image Upload and Media Library APIs.
Verifies secure image upload, listing, sanitization, core asset protection, and deletion.
"""

import os
import io
import json
import unittest
import server

class TestAdminImageUpload(unittest.TestCase):
    def setUp(self):
        server.app.config['TESTING'] = True
        self.ctx = server.app.app_context()
        self.ctx.push()
        self.client = server.app.test_client()

        # Create admin test session
        db = server.get_db()
        cur = db.cursor()
        cur.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
        row = cur.fetchone()
        if not row:
            # Create a test admin user
            cur.execute("""
                INSERT INTO users (name, email, role, status, provider, created_at)
                VALUES ('Admin Test', 'admin_upload_test@viccollege.com', 'admin', 'active', 'email', '2026-09-26T00:00:00')
            """)
            db.commit()
            self.admin_user_id = cur.lastrowid
        else:
            self.admin_user_id = row['id']

        self.token = server.create_user_session(self.admin_user_id)
        self.headers = {
            'Authorization': f'Bearer {self.token}'
        }
        self.test_uploaded_files = []

    def tearDown(self):
        # Clean up any test files created in images/
        images_dir = os.path.join(server.BASE_DIR, 'images')
        for filename in self.test_uploaded_files:
            file_path = os.path.join(images_dir, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
        self.ctx.pop()

    def test_get_images_list(self):
        """Test listing existing images in images/ folder."""
        res = self.client.get('/api/admin/images', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data.decode('utf-8'))
        self.assertTrue(data.get('success'))
        self.assertIn('images', data)
        self.assertGreater(data.get('count', 0), 0)

        # Check structure of image items
        sample = data['images'][0]
        self.assertIn('filename', sample)
        self.assertIn('path', sample)
        self.assertIn('size_kb', sample)
        self.assertIn('is_core', sample)

    def test_upload_image_success(self):
        """Test uploading a new image to images/ directory."""
        fake_png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        test_filename = 'test_program_badge_2026.png'
        self.test_uploaded_files.append(test_filename)

        data = {
            'image': (io.BytesIO(fake_png_data), test_filename),
            'custom_name': 'test_program_badge_2026'
        }

        res = self.client.post(
            '/api/admin/upload-image',
            headers=self.headers,
            data=data,
            content_type='multipart/form-data'
        )

        self.assertEqual(res.status_code, 200)
        res_json = json.loads(res.data.decode('utf-8'))
        self.assertTrue(res_json.get('success'))
        self.assertEqual(res_json.get('url'), f'images/{test_filename}')
        
        # Verify file actually exists in images/
        saved_path = os.path.join(server.BASE_DIR, 'images', test_filename)
        self.assertTrue(os.path.exists(saved_path))

        # Verify it can be served via GET /images/<filename>
        static_res = self.client.get(f'/images/{test_filename}')
        self.assertEqual(static_res.status_code, 200)

    def test_upload_invalid_extension(self):
        """Test that non-image extensions (.exe, .py, .sh) are rejected."""
        data = {
            'image': (io.BytesIO(b'malicious script'), 'bad_file.exe')
        }
        res = self.client.post(
            '/api/admin/upload-image',
            headers=self.headers,
            data=data,
            content_type='multipart/form-data'
        )
        self.assertEqual(res.status_code, 400)
        res_json = json.loads(res.data.decode('utf-8'))
        self.assertIn('error', res_json)

    def test_core_image_protection(self):
        """Test that core system assets cannot be deleted."""
        res = self.client.delete('/api/admin/images/vic_logo.png', headers=self.headers)
        self.assertEqual(res.status_code, 403)
        res_json = json.loads(res.data.decode('utf-8'))
        self.assertIn('protected', res_json.get('error', ''))

    def test_delete_uploaded_image(self):
        """Test deleting an uploaded image."""
        test_filename = 'temp_delete_test.jpg'
        file_path = os.path.join(server.BASE_DIR, 'images', test_filename)
        with open(file_path, 'wb') as f:
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00')

        self.test_uploaded_files.append(test_filename)
        self.assertTrue(os.path.exists(file_path))

        res = self.client.delete(f'/api/admin/images/{test_filename}', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(os.path.exists(file_path))

if __name__ == '__main__':
    unittest.main()
