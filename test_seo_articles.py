"""
Integration test for Super Admin AI Keyword Article Generator & GEO/SEO Sitemap Management
"""
import unittest
import json
import sqlite3
import os
import server

class TestSEOArticlesAndSitemap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()
        server.init_database()

    def get_admin_token(self, email="mack.chen@viccollege.com", password="admin123"):
        res = self.client.post('/api/auth/login', json={
            'email': email,
            'password': password
        })
        data = res.get_json() or {}
        self.assertIn('token', data, f"Admin login must return token. Got response: {data}")
        return data['token']

    def test_01_article_generation_defaults_to_hidden(self):
        """Test that AI/Keyword article generation sets status='hidden' and is_active=0 by default."""
        token = self.get_admin_token()
        res = self.client.post('/api/admin/articles/generate', 
            headers={'Authorization': f'Bearer {token}'},
            json={
                'keywords': 'Electrician 309A apprenticeship Markham, Ontario trades grants $28000',
                'geo_target': 'Markham & GTA, Ontario',
                'category': 'programs',
                'language': 'en',
                'tone': 'Career Changers & Job Seekers'
            }
        )
        self.assertIn(res.status_code, [200, 201], f"Expected 200 or 201, got {res.status_code} with body: {res.get_json()}")
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('article', data)
        art = data['article']

        # CRITICAL USER REQUIREMENT: Article is HIDDEN by default
        self.assertEqual(art['status'], 'hidden', "New article MUST be hidden by default")
        self.assertEqual(art['is_active'], 0, "New article MUST have is_active=0")
        self.assertEqual(art['geo_target'], 'Markham & GTA, Ontario')
        self.assertIsNotNone(art['geo_lat'])
        self.assertIsNotNone(art['geo_lng'])
        self.assertTrue(len(art['title']) > 15, "Article title must be comprehensive")
        self.assertTrue(len(art['content']) > 100, "Article content must be detailed")

        # Store ID and slug on class for subsequent tests
        TestSEOArticlesAndSitemap.created_article_id = art['id']
        TestSEOArticlesAndSitemap.created_slug = art['slug']

    def test_02_hidden_articles_excluded_from_public_api_and_sitemap(self):
        """Test that newly generated hidden articles do NOT appear in public API or sitemap.xml."""
        slug = getattr(self, 'created_slug', 'electrician-309a-apprenticeship-markham')
        
        # 1. Public API list
        res = self.client.get('/api/articles')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        public_slugs = [a['slug'] for a in data.get('articles', [])]
        self.assertNotIn(slug, public_slugs, "Hidden article MUST NOT appear in public /api/articles list")

        # 2. Public API single item (anonymous visitor)
        res_single = self.client.get(f'/api/articles/{slug}')
        self.assertEqual(res_single.status_code, 404, "Anonymous visitor accessing hidden article directly gets 404")

        # 3. Dynamic Sitemap XML
        res_sitemap = self.client.get('/sitemap.xml')
        self.assertEqual(res_sitemap.status_code, 200)
        sitemap_xml = res_sitemap.data.decode('utf-8')
        self.assertNotIn(f'<loc>http://localhost:5055/article.html?slug={slug}</loc>', sitemap_xml, 
            "Hidden article MUST NOT be indexed in /sitemap.xml")

    def test_03_super_admin_can_toggle_activate_article(self):
        """Test Super Admin activating the article with 1-click, making it visible on live site and sitemap."""
        token = self.get_admin_token()
        art_id = getattr(self, 'created_article_id', None)
        self.assertIsNotNone(art_id)

        # 1. Toggle status to ACTIVE
        res = self.client.patch(f'/api/admin/articles/{art_id}/toggle-status',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['is_active'], 1)

        # 2. Verify it NOW appears in public /api/articles
        res_pub = self.client.get('/api/articles')
        pub_data = res_pub.get_json()
        active_ids = [a['id'] for a in pub_data.get('articles', [])]
        self.assertIn(art_id, active_ids, "Activated article MUST appear in public /api/articles")

        # 3. Verify it NOW appears in /sitemap.xml with GEO coordinates
        res_sitemap = self.client.get('/sitemap.xml')
        sitemap_xml = res_sitemap.data.decode('utf-8')
        slug = getattr(self, 'created_slug')
        self.assertIn(f'/article.html?slug={slug}', sitemap_xml, "Activated article MUST be in /sitemap.xml")
        self.assertIn('<geo:geo>', sitemap_xml, "Sitemap must include Google Geo extension tags")

    def test_04_super_admin_can_toggle_hide_article_again(self):
        """Test Super Admin hiding the article again, instantly removing it from site and sitemap."""
        token = self.get_admin_token()
        art_id = getattr(self, 'created_article_id', None)

        # 1. Toggle status back to HIDDEN
        res = self.client.patch(f'/api/admin/articles/{art_id}/toggle-status',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'hidden')
        self.assertEqual(data['is_active'], 0)

        # 2. Verify removed from public /api/articles
        res_pub = self.client.get('/api/articles')
        active_ids = [a['id'] for a in res_pub.get_json().get('articles', [])]
        self.assertNotIn(art_id, active_ids, "Hidden article MUST NOT appear in /api/articles")

        # 3. Verify removed from /sitemap.xml
        res_sitemap = self.client.get('/sitemap.xml')
        sitemap_xml = res_sitemap.data.decode('utf-8')
        slug = getattr(self, 'created_slug')
        self.assertNotIn(f'/article.html?slug={slug}', sitemap_xml, "Hidden article MUST be excluded from /sitemap.xml")

    def test_05_manual_sitemap_generation_endpoint(self):
        """Test /api/admin/sitemap/generate returns metrics and regenerated XML."""
        token = self.get_admin_token()
        res = self.client.post('/api/admin/sitemap/generate',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['total_urls'], 5)
        self.assertIn('xml_preview', data)

    def test_06_super_admin_preview_access_to_hidden_article(self):
        """Test Super Admin can preview hidden drafts with preview flag."""
        token = self.get_admin_token()
        slug = getattr(self, 'created_slug')
        res = self.client.get(f'/api/articles/{slug}',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['article']['is_preview'])

if __name__ == '__main__':
    unittest.main()
