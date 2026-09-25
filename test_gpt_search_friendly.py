"""
Test suite for GPT Search, AI Crawlers, and Generative Engine Optimization (GEO) friendliness:
1. Dynamic /robots.txt with AI search bot directives (OAI-SearchBot, GPTBot, Perplexity, Claude, etc.)
2. Standard Markdown /llms.txt and /llms-full.txt documents per llmstxt.org specification
3. Direct crawlable Knowledge Base URLs in /sitemap.xml (https://viccollege.ca/article.html?kb={id})
4. Public API endpoint GET /api/knowledge/<id>
5. Schema.org JSON-LD structured data for College, Programs, Articles, and FAQs
"""
import unittest
import os
import xml.etree.ElementTree as ET
import server

class TestGPTSearchFriendly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()
        server.init_database()

    def test_01_robots_txt_ai_crawlers_and_sitemap(self):
        """Verify robots.txt explicitly permits all major AI search bots and points to sitemap and llms.txt."""
        res = self.client.get('/robots.txt')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/plain', res.headers.get('Content-Type', ''))
        content = res.data.decode('utf-8')

        # Check AI Bot User-Agents
        ai_bots = [
            'OAI-SearchBot',
            'GPTBot',
            'ChatGPT-User',
            'PerplexityBot',
            'ClaudeBot',
            'Google-Extended',
            'Googlebot',
            'Bingbot',
            'Applebot'
        ]
        for bot in ai_bots:
            self.assertIn(f'User-agent: {bot}', content, f"robots.txt must declare User-agent: {bot}")

        # Check Sitemap & LLM References
        self.assertIn('Sitemap: https://viccollege.ca/sitemap.xml', content)
        self.assertIn('https://viccollege.ca/llms.txt', content)

        # Check disk file
        robots_disk_path = os.path.join(server.BASE_DIR, 'robots.txt')
        self.assertTrue(os.path.exists(robots_disk_path), "robots.txt must exist on disk")
        with open(robots_disk_path, 'r', encoding='utf-8') as f:
            disk_content = f.read()
        self.assertEqual(disk_content.strip(), content.strip())

    def test_02_llms_txt_standard_context_document(self):
        """Verify llms.txt generates high-density Markdown context for LLMs."""
        res = self.client.get('/llms.txt')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/plain', res.headers.get('Content-Type', ''))
        content = res.data.decode('utf-8')

        # Core Institutional Grounding
        self.assertIn("# Victoria International College of Business & Technology", content)
        self.assertIn("Ontario Career Colleges Act, 2005", content)
        self.assertIn("7050 Woodbine Ave.", content)
        self.assertIn("416-665-6668", content)
        self.assertIn("info@viccollege.com", content)
        self.assertIn("https://viccollege.ca/sitemap.xml", content)

        # Financial Aid & Grants ($28,000+)
        self.assertIn("Better Jobs Ontario", content)
        self.assertIn("$28,000+", content)

        # Academic Programs
        self.assertIn("## Academic Diploma Programs", content)
        self.assertIn("personal-support-worker-online-psw-course.html", content)
        self.assertIn("software-development.html", content)
        self.assertIn("computerized-accounting.html", content)

        # Knowledge Base Q&As with crawlable URLs
        self.assertIn("## Knowledge Base & Frequently Asked Questions", content)
        self.assertIn("https://viccollege.ca/article.html?kb=", content)

        # Policies
        self.assertIn("## Regulatory & Compliance Policies", content)
        self.assertIn("kpi-audit-requirements.html", content)
        self.assertIn("sexual-violence-policy.html", content)

        # Check disk file
        llms_disk_path = os.path.join(server.BASE_DIR, 'llms.txt')
        self.assertTrue(os.path.exists(llms_disk_path), "llms.txt must exist on disk")

    def test_03_llms_full_txt_deep_grounding_document(self):
        """Verify llms-full.txt contains full-length un-truncated answers."""
        res = self.client.get('/llms-full.txt')
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/plain', res.headers.get('Content-Type', ''))
        content = res.data.decode('utf-8')

        self.assertIn("# Victoria International College of Business & Technology", content)
        self.assertIn("## Knowledge Base & Frequently Asked Questions", content)
        self.assertIn("https://viccollege.ca/article.html?kb=", content)

        llms_full_disk_path = os.path.join(server.BASE_DIR, 'llms-full.txt')
        self.assertTrue(os.path.exists(llms_full_disk_path), "llms-full.txt must exist on disk")

    def test_04_sitemap_xml_crawlable_kb_and_geo_tags(self):
        """Verify sitemap.xml uses crawlable article.html?kb={id} and geo:geo tags."""
        res = self.client.get('/sitemap.xml')
        self.assertEqual(res.status_code, 200)
        self.assertIn('application/xml', res.headers.get('Content-Type', ''))
        xml_content = res.data.decode('utf-8')

        root = ET.fromstring(xml_content)
        urls = [elem.text for elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]

        # 1. Check direct crawlable KB URLs (not # fragments)
        with server.app.app_context():
            db = server.get_db()
            kb_rows = db.execute("SELECT id FROM knowledge_base").fetchall()
            for r in kb_rows:
                expected_kb_url = f"https://viccollege.ca/article.html?kb={r['id']}"
                self.assertIn(expected_kb_url, urls, f"Sitemap must contain direct crawlable URL: {expected_kb_url}")

        # 2. Check Geo XML tags
        self.assertIn('xmlns:geo="http://www.google.com/geo/schemas/sitemap/1.0"', xml_content)
        self.assertIn('<geo:geo>', xml_content)
        self.assertIn('<geo:lat>', xml_content)
        self.assertIn('<geo:long>', xml_content)

        # 3. Check Institutional & Program Pages
        self.assertIn('https://viccollege.ca/', urls)
        self.assertIn('https://viccollege.ca/personal-support-worker-online-psw-course.html', urls)
        self.assertIn('https://viccollege.ca/software-development.html', urls)

    def test_05_public_knowledge_item_api(self):
        """Verify GET /api/knowledge/<id> returns formatted knowledge and article models."""
        with server.app.app_context():
            db = server.get_db()
            row = db.execute("SELECT id, title, content FROM knowledge_base LIMIT 1").fetchone()
            self.assertIsNotNone(row)
            kb_id = row['id']
            kb_title = row['title']

        res = self.client.get(f'/api/knowledge/{kb_id}')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertTrue(data['success'])
        self.assertIn('knowledge', data)
        self.assertIn('article', data)
        self.assertEqual(data['article']['id'], kb_id)
        self.assertEqual(data['article']['title'], kb_title)
        self.assertEqual(data['article']['slug'], f'kb-{kb_id}')
        self.assertEqual(data['article']['geo_target'], 'Toronto & Markham, Ontario')
        self.assertEqual(data['article']['geo_lat'], 43.8561)

        # Test non-existent ID returns 404
        res_404 = self.client.get('/api/knowledge/999999')
        self.assertEqual(res_404.status_code, 404)

    def test_06_index_and_program_html_schema_org_json_ld(self):
        """Verify index.html and program HTML pages contain valid Schema.org JSON-LD."""
        index_path = os.path.join(server.BASE_DIR, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            index_html = f.read()

        self.assertIn('application/ld+json', index_html)
        self.assertIn('"@type": "CollegeOrUniversity"', index_html)
        self.assertIn('Victoria International College of Business & Technology', index_html)
        self.assertIn('7050 Woodbine Ave.', index_html)
        self.assertIn('Better Jobs Ontario', index_html)

        # Check PSW page
        psw_path = os.path.join(server.BASE_DIR, 'personal-support-worker-online-psw-course.html')
        with open(psw_path, 'r', encoding='utf-8') as f:
            psw_html = f.read()
        self.assertIn('application/ld+json', psw_html)
        self.assertIn('"@type": "EducationalOccupationalProgram"', psw_html)
        self.assertIn('NACC Personal Support Worker', psw_html)

        # Check Article page script logic
        art_path = os.path.join(server.BASE_DIR, 'article.html')
        with open(art_path, 'r', encoding='utf-8') as f:
            art_html = f.read()
        self.assertIn('urlParams.get(\'kb\')', art_html)
        self.assertIn('/api/knowledge/', art_html)
        self.assertIn('"@type": "FAQPage"', art_html)

if __name__ == '__main__':
    unittest.main()
