"""
Integration tests for Dynamic Academic Programs Management and Public APIs.
"""
import unittest
import json
import sqlite3
import os
import server

class TestDynamicProgramsAPI(unittest.TestCase):
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

    def test_01_public_programs_list(self):
        """Test that public GET /api/programs returns active programs seeded in order."""
        res = self.client.get('/api/programs')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('programs', data)
        self.assertGreaterEqual(len(data['programs']), 6)
        
        # Verify the 6 programs slugs are present
        slugs = [p['slug'] for p in data['programs']]
        for expected_slug in ['psw', 'accounting', 'eca', 'acupuncture', 'electrician', 'tech']:
            self.assertIn(expected_slug, slugs)

        # Check full stack web technician is present with modules and bullets parsed
        tech_prog = next(p for p in data['programs'] if p['slug'] == 'tech')
        self.assertIsInstance(tech_prog['bullets_en'], list)
        self.assertIsInstance(tech_prog['modules_en'], list)
        self.assertGreater(len(tech_prog['bullets_en']), 0)
        self.assertGreater(len(tech_prog['modules_en']), 0)

    def test_02_public_program_by_slug_and_id(self):
        """Test that public GET /api/programs/<identifier> works for both slug and ID."""
        # Query by slug
        res = self.client.get('/api/programs/psw')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['program']['slug'], 'psw')
        self.assertIn('NACC', data['program']['title_en'])

        # Query by ID
        prog_id = data['program']['id']
        res2 = self.client.get(f'/api/programs/{prog_id}')
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertEqual(data2['program']['id'], prog_id)

    def test_03_admin_programs_crud_lifecycle(self):
        """Test Admin create, read, update, toggle status, and delete program."""
        token = self.get_admin_token()
        headers = {'Authorization': f'Bearer {token}'}

        # 1. Admin GET /api/admin/programs
        res = self.client.get('/api/admin/programs', headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        initial_count = len(data['programs'])

        # 2. Admin POST /api/admin/programs (Create a new program)
        new_prog = {
            'slug': 'cloud-devops',
            'category': 'technology',
            'image_url': 'images/fullstack.jpg',
            'badge_en': 'Cloud Engineering • Career Diploma',
            'badge_zh': '云架构与运维 • 高薪文凭',
            'title_en': 'Cloud DevOps & Infrastructure Engineer',
            'title_zh': '云原生架构与 DevOps 工程师',
            'desc_en': 'Comprehensive hands-on training on AWS, Kubernetes, Terraform, and CI/CD pipelines.',
            'desc_zh': '深入掌握 AWS、Kubernetes、Terraform 及 CI/CD 自动化流水线。',
            'bullets_en': ['AWS Certified Solutions', 'Kubernetes & Docker', 'Terraform IaC', 'CI/CD Automation'],
            'bullets_zh': ['AWS 认证架构师', 'K8s 容器编排', 'Terraform 基础设施即代码', 'CI/CD 自动化流水线'],
            'duration_en': '24 Weeks (Part-time Labs)',
            'duration_zh': '24 周（实战机房）',
            'credential_en': 'Cloud DevOps Diploma',
            'credential_zh': '云原生 DevOps 职业文凭',
            'overview_en': 'Master modern infrastructure automation and cloud deployments with enterprise mentors.',
            'overview_zh': '名师手把手带教现代云端基础设施与企业级 DevOps 自动化实战。',
            'modules_en': ['Linux Fundamentals', 'AWS Core Services', 'Docker & Kubernetes', 'Infrastructure as Code'],
            'modules_zh': ['Linux 运维基础', 'AWS 核心云服务', 'Docker 与 K8s 容器化', 'IaC 自动化代码化运维'],
            'careers_en': 'DevOps Engineer, Cloud Architect, Site Reliability Engineer',
            'careers_zh': 'DevOps 工程师、云架构师、SRE 网站可靠性工程师',
            'outcomes_en': 'Average entry salary $75,000–$95,000/year.',
            'outcomes_zh': '起薪约 $75,000–$95,000/年，加国市场刚需。',
            'display_order': 99,
            'is_active': 1
        }

        res = self.client.post('/api/admin/programs', headers=headers, json=new_prog)
        self.assertEqual(res.status_code, 201)
        created_data = res.get_json()
        self.assertTrue(created_data['success'])
        prog_id = created_data['program']['id']
        self.assertEqual(created_data['program']['slug'], 'cloud-devops')

        # 3. Verify it is visible in public /api/programs
        res = self.client.get('/api/programs')
        slugs = [p['slug'] for p in res.get_json()['programs']]
        self.assertIn('cloud-devops', slugs)

        # 4. Admin PUT /api/admin/programs/<id> (Update program)
        update_payload = dict(new_prog)
        update_payload['title_en'] = 'Advanced Cloud DevOps & AI Infrastructure Engineer'
        res = self.client.put(f'/api/admin/programs/{prog_id}', headers=headers, json=update_payload)
        self.assertEqual(res.status_code, 200)
        updated_data = res.get_json()
        self.assertEqual(updated_data['program']['title_en'], 'Advanced Cloud DevOps & AI Infrastructure Engineer')

        # 5. Admin PATCH /api/admin/programs/<id>/toggle-status (Make Inactive)
        res = self.client.patch(f'/api/admin/programs/{prog_id}/toggle-status', headers=headers)
        self.assertEqual(res.status_code, 200)
        toggle_data = res.get_json()
        self.assertEqual(toggle_data['is_active'], 0)

        # Verify inactive program is excluded from public GET /api/programs
        res = self.client.get('/api/programs')
        public_slugs = [p['slug'] for p in res.get_json()['programs']]
        self.assertNotIn('cloud-devops', public_slugs)

        # 6. Admin DELETE /api/admin/programs/<id>
        res = self.client.delete(f'/api/admin/programs/{prog_id}', headers=headers)
        self.assertEqual(res.status_code, 200)
        del_data = res.get_json()
        self.assertTrue(del_data['success'])

        # Verify it is completely removed
        res = self.client.get(f'/api/admin/programs/{prog_id}', headers=headers)
        self.assertEqual(res.status_code, 404)

    def test_04_admin_programs_reordering(self):
        """Test Admin reorder API properly updates display_order across multiple programs."""
        token = self.get_admin_token()
        headers = {'Authorization': f'Bearer {token}'}

        res = self.client.get('/api/admin/programs', headers=headers)
        programs = res.get_json()['programs']
        self.assertGreaterEqual(len(programs), 6)

        # Reverse the order of IDs
        reversed_ids = [p['id'] for p in reversed(programs)]
        res = self.client.post('/api/admin/programs/reorder', headers=headers, json={
            'ordered_ids': reversed_ids
        })
        self.assertEqual(res.status_code, 200)

        # Check new order in public API
        res = self.client.get('/api/programs')
        new_programs = res.get_json()['programs']
        new_ids = [p['id'] for p in new_programs]
        self.assertEqual(new_ids[0], reversed_ids[0])

        # Restore original order (order by default IDs 1..6)
        sorted_ids = sorted([p['id'] for p in programs])
        res = self.client.post('/api/admin/programs/reorder', headers=headers, json={
            'ordered_ids': sorted_ids
        })
        self.assertEqual(res.status_code, 200)

    def test_05_admin_stats_includes_programs(self):
        """Test GET /api/admin/stats returns accurate total_programs and active_programs."""
        token = self.get_admin_token()
        headers = {'Authorization': f'Bearer {token}'}

        res = self.client.get('/api/admin/stats', headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total_programs', data)
        self.assertIn('active_programs', data)
        self.assertGreaterEqual(data['total_programs'], 6)
        self.assertGreaterEqual(data['active_programs'], 6)

if __name__ == '__main__':
    unittest.main()
