"""
Integration tests verifying instant dynamic Sitemap XML updates whenever an item
is added, modified, toggled, or deleted across:
  1. Knowledge Base articles
  2. SEO & GEO Articles
  3. Job Fair & Event Banners
  4. Academic Programs
"""
import unittest
import json
import os
import xml.etree.ElementTree as ET
import server

class TestSitemapAutoSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()
        server.init_database()

    def get_admin_headers(self):
        res = self.client.post('/api/auth/login', json={
            'email': 'mack.chen@viccollege.com',
            'password': 'admin123'
        })
        data = res.get_json() or {}
        token = data.get('token')
        return {'Authorization': f'Bearer {token}'}

    def get_current_sitemap(self):
        res = self.client.get('/sitemap.xml')
        self.assertEqual(res.status_code, 200)
        xml_content = res.data.decode('utf-8')
        root = ET.fromstring(xml_content)
        urls = [elem.text for elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        return xml_content, urls

    def test_01_academic_programs_add_and_delete_sitemap_sync(self):
        """Test adding and deleting an Academic Program immediately updates sitemap.xml."""
        headers = self.get_admin_headers()
        slug = "cybersecurity-specialist-test"

        # 1. Create a new program
        new_prog = {
            'title_en': 'Cybersecurity Specialist Diploma',
            'title_zh': '网络安全专家大专文凭',
            'slug': slug,
            'category': 'tech',
            'desc_en': 'Defend modern enterprise infrastructures.',
            'desc_zh': '保护现代企业数字基础设施安全。',
            'bullets_en': ['Network Defense', 'Ethical Hacking', 'SOC Operations'],
            'is_active': 1
        }
        res_create = self.client.post('/api/admin/programs', headers=headers, json=new_prog)
        self.assertEqual(res_create.status_code, 201)
        prog_id = res_create.get_json()['id']

        # 2. Check sitemap has the new program URL
        xml_content, urls = self.get_current_sitemap()
        expected_url = f'https://viccollege.ca/#programs-{slug}'
        self.assertIn(expected_url, urls, "Newly created academic program must be in sitemap.xml immediately")

        # Also check file on disk
        sitemap_file_path = os.path.join(server.BASE_DIR, 'sitemap.xml')
        with open(sitemap_file_path, 'r', encoding='utf-8') as f:
            disk_content = f.read()
        self.assertIn(expected_url, disk_content, "sitemap.xml on disk must reflect newly created program")

        # 3. Delete the program
        res_del = self.client.delete(f'/api/admin/programs/{prog_id}', headers=headers)
        self.assertEqual(res_del.status_code, 200)

        # 4. Check sitemap no longer contains the program URL
        xml_content_after, urls_after = self.get_current_sitemap()
        self.assertNotIn(expected_url, urls_after, "Deleted academic program must be removed from sitemap.xml immediately")

    def test_02_knowledge_base_add_and_delete_sitemap_sync(self):
        """Test adding and deleting a Knowledge Base article immediately updates sitemap.xml."""
        headers = self.get_admin_headers()

        # 1. Create KB article
        res_kb = self.client.post('/api/admin/knowledge', headers=headers, json={
            'title': 'How to apply for Second Career in Markham',
            'category': 'financial_aid',
            'keywords': 'grant, second career, markham, financial aid',
            'content': 'Comprehensive guide on applying for grants at Markham Campus.',
            'priority': 5,
            'is_active': 1
        })
        self.assertEqual(res_kb.status_code, 200)
        kb_id = res_kb.get_json()['id']

        # 2. Verify sitemap includes the new KB URL
        expected_kb_url = f'https://viccollege.ca/article.html?kb={kb_id}'
        _, urls = self.get_current_sitemap()
        self.assertIn(expected_kb_url, urls, "Newly added KB article must be immediately in sitemap.xml")

        # 3. Delete KB article
        res_del = self.client.delete(f'/api/admin/knowledge/{kb_id}', headers=headers)
        self.assertEqual(res_del.status_code, 200)

        # 4. Verify sitemap removes the KB URL
        _, urls_after = self.get_current_sitemap()
        self.assertNotIn(expected_kb_url, urls_after, "Deleted KB article must be removed from sitemap.xml")

    def test_03_seo_article_generate_and_delete_sitemap_sync(self):
        """Test generating and deleting an SEO & GEO article immediately updates sitemap.xml."""
        headers = self.get_admin_headers()

        # 1. Generate article
        res_art = self.client.post('/api/admin/articles/generate', headers=headers, json={
            'keywords': 'Best Full Stack Web Technician Program Markham',
            'geo_target': 'Markham & York Region, Ontario',
            'category': 'programs',
            'language': 'en'
        })
        self.assertEqual(res_art.status_code, 200)
        art_id = res_art.get_json()['id']
        slug = res_art.get_json()['article']['slug']

        # 2. Verify sitemap includes the generated article
        expected_art_url = f'https://viccollege.ca/article.html?slug={slug}'
        xml_str, urls = self.get_current_sitemap()
        self.assertIn(expected_art_url, urls, "Generated SEO & GEO article must be immediately indexed in sitemap.xml")
        self.assertIn('<geo:geo>', xml_str, "Sitemap must include geo coordinates")

        # 3. Delete article
        res_del = self.client.delete(f'/api/admin/articles/{art_id}', headers=headers)
        self.assertEqual(res_del.status_code, 200)

        # 4. Verify sitemap removes the article URL
        _, urls_after = self.get_current_sitemap()
        self.assertNotIn(expected_art_url, urls_after, "Deleted article must be removed from sitemap.xml")

    def test_04_job_fair_add_and_delete_sitemap_sync(self):
        """Test creating and deleting a Job Fair event immediately updates sitemap.xml."""
        headers = self.get_admin_headers()

        # 1. Create Job Fair event
        res_jf = self.client.post('/api/admin/job-fairs', headers=headers, json={
            'title_en': '2026 Ontario Tech & Healthcare Career Mega Fair',
            'title_zh': '2026 安省高科技与医疗健康大型招聘会',
            'subtitle_en': 'Meet 60+ top employers hiring on site.',
            'subtitle_zh': '现场对接60余家顶尖雇主招聘。',
            'date_en': 'Saturday, Nov 14, 2026 (1:00 PM - 5:00 PM)',
            'date_zh': '2026年11月14日 周六 (1:00 PM - 5:00 PM)',
            'location_en': '7050 Woodbine Ave., Markham, ON',
            'location_zh': '万锦主校区 7050 Woodbine Ave., Markham',
            'is_active': 1
        })
        self.assertEqual(res_jf.status_code, 201)
        event_id = res_jf.get_json()['job_fair']['id']

        # 2. Verify sitemap includes the new job fair event
        expected_jf_url = f'https://viccollege.ca/#job-fair-event-{event_id}'
        _, urls = self.get_current_sitemap()
        self.assertIn(expected_jf_url, urls, "Newly created job fair event must be immediately in sitemap.xml")

        # 3. Delete Job Fair event
        res_del = self.client.delete(f'/api/admin/job-fairs/{event_id}', headers=headers)
        self.assertEqual(res_del.status_code, 200)

        # 4. Verify sitemap removes the job fair event
        _, urls_after = self.get_current_sitemap()
        self.assertNotIn(expected_jf_url, urls_after, "Deleted job fair event must be removed from sitemap.xml")

        # 5. Restore active status for seeded event so other test suites remain green
        with server.app.app_context():
            db = server.get_db()
            db.execute("UPDATE job_fairs SET is_active = 1 WHERE id = (SELECT MIN(id) FROM job_fairs)")
            db.commit()

if __name__ == '__main__':
    unittest.main()
