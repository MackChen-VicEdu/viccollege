"""
Unit & Integration Tests for Automated Database Backup and Deployment Migration
Tests:
1. Automated timestamped backup generation on deployment
2. Backup rotation & pruning (retaining max_keep files)
3. Schema synchronization (new tables & columns)
4. Master CMS content synchronization (programs, articles, Q&As, job fairs, translations, settings)
5. Zero data loss guarantee for live production tables (consultations, users, sessions, chat_logs)
6. Secret credential preservation in production settings
7. Startup auto-deploy idempotency
"""

import os
import sys
import shutil
import sqlite3
import unittest
import tempfile
from datetime import datetime

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import manage_db


class TestAutoDeployDB(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="vic_deploy_test_")
        self.backups_dir = os.path.join(self.test_dir, "backups")
        os.makedirs(self.backups_dir, exist_ok=True)

        self.dev_db_path = os.path.join(self.test_dir, "dev.db")
        self.prod_db_path = os.path.join(self.test_dir, "prod.db")

        # 1. Create Prod DB with live user data
        conn_prod = sqlite3.connect(self.prod_db_path)
        cur_prod = conn_prod.cursor()

        # Schema & live tables
        cur_prod.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                role TEXT
            )
        """)
        cur_prod.execute("""
            CREATE TABLE consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                program TEXT
            )
        """)
        cur_prod.execute("""
            CREATE TABLE sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TEXT
            )
        """)
        cur_prod.execute("""
            CREATE TABLE chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                message TEXT
            )
        """)
        cur_prod.execute("""
            CREATE TABLE programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE,
                name_en TEXT,
                tuition_fee INTEGER
            )
        """)
        cur_prod.execute("""
            CREATE TABLE site_translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                category TEXT,
                text_en TEXT,
                text_zh TEXT,
                updated_at TEXT
            )
        """)
        cur_prod.execute("""
            CREATE TABLE settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)

        # Insert live production data
        cur_prod.execute("INSERT INTO users (name, email, role) VALUES ('Live Student', 'live@student.com', 'user')")
        cur_prod.execute("INSERT INTO consultations (name, email, phone, program) VALUES ('Inquiry Jane', 'jane@test.com', '416-111-2222', 'psw')")
        cur_prod.execute("INSERT INTO sessions (token, user_id, created_at) VALUES ('live_token_123', 1, '2026-10-10')")
        cur_prod.execute("INSERT INTO chat_logs (session_id, message) VALUES ('live_token_123', 'Hello, tell me about grants')")

        # Insert existing program and live production secret key
        cur_prod.execute("INSERT INTO programs (slug, name_en, tuition_fee) VALUES ('psw', 'PSW Old Title', 5000)")
        cur_prod.execute("INSERT INTO settings (key, value, updated_at) VALUES ('openai_api_key', 'sk-live-prod-secret-key-12345', '2026-10-10')")
        cur_prod.execute("INSERT INTO settings (key, value, updated_at) VALUES ('openai_model', 'gpt-4o-mini', '2026-10-10')")

        conn_prod.commit()
        conn_prod.close()

        # 2. Create Dev DB with updates & new schema additions
        conn_dev = sqlite3.connect(self.dev_db_path)
        cur_dev = conn_dev.cursor()

        cur_dev.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                role TEXT
            )
        """)
        cur_dev.execute("""
            CREATE TABLE consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                phone TEXT,
                program TEXT
            )
        """)
        cur_dev.execute("""
            CREATE TABLE sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TEXT
            )
        """)
        cur_dev.execute("""
            CREATE TABLE chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                message TEXT
            )
        """)
        # Dev has updated programs table with a new column: job_placement_rate
        cur_dev.execute("""
            CREATE TABLE programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE,
                name_en TEXT,
                tuition_fee INTEGER,
                job_placement_rate TEXT
            )
        """)
        # Dev has a brand new table: campus_announcements
        cur_dev.execute("""
            CREATE TABLE campus_announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT
            )
        """)
        cur_dev.execute("""
            CREATE TABLE site_translations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                category TEXT,
                text_en TEXT,
                text_zh TEXT,
                updated_at TEXT
            )
        """)
        cur_dev.execute("""
            CREATE TABLE settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        """)

        # Dev CMS records
        cur_dev.execute("INSERT INTO programs (slug, name_en, tuition_fee, job_placement_rate) VALUES ('psw', 'Personal Support Worker (PSW)', 5500, '95%')")
        cur_dev.execute("INSERT INTO programs (slug, name_en, tuition_fee, job_placement_rate) VALUES ('full-stack', 'Full Stack Developer', 8000, '92%')")
        cur_dev.execute("INSERT INTO campus_announcements (title, content) VALUES ('Fall Open House', 'Join us on Saturday')")
        cur_dev.execute("INSERT INTO site_translations (key, category, text_en, text_zh, updated_at) VALUES ('header.tagline', 'nav', 'Excellence in Education', '卓越教育', '2026-10-10')")

        # Dev settings: Sanitized empty openai_api_key, and an updated model + new setting
        cur_dev.execute("INSERT INTO settings (key, value, updated_at) VALUES ('openai_api_key', '', '2026-10-10')")
        cur_dev.execute("INSERT INTO settings (key, value, updated_at) VALUES ('openai_model', 'gpt-4o', '2026-10-10')")
        cur_dev.execute("INSERT INTO settings (key, value, updated_at) VALUES ('enable_voice_chat', 'true', '2026-10-10')")

        conn_dev.commit()
        conn_dev.close()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_backup_pruning(self):
        """Test backup pruning safely deletes oldest files beyond max_keep."""
        # Create 10 dummy backup files
        for i in range(10):
            f_path = os.path.join(self.backups_dir, f"backup_{i:02d}.db")
            with open(f_path, "w") as f:
                f.write(f"backup {i}")
            # Ensure staggered mtimes
            os.utime(f_path, (1000 + i * 10, 1000 + i * 10))

        initial_count = len(os.listdir(self.backups_dir))
        self.assertEqual(initial_count, 10)

        # Prune keeping latest 4
        deleted = manage_db.prune_backups(max_keep=4, backups_dir=self.backups_dir)
        self.assertEqual(deleted, 6)

        remaining = sorted(os.listdir(self.backups_dir))
        self.assertEqual(len(remaining), 4)
        # Oldest were backup_00 .. backup_05; newest 4 should remain (06, 07, 08, 09)
        self.assertIn("backup_09.db", remaining)
        self.assertIn("backup_08.db", remaining)
        self.assertNotIn("backup_00.db", remaining)

    def test_deployment_sync_and_backup(self):
        """Test full deployment pipeline: backup, schema evolution, CMS sync, user data safety."""
        # Save original BACKUPS_DIR and override to test directory
        original_backups_dir = manage_db.BACKUPS_DIR
        manage_db.BACKUPS_DIR = self.backups_dir

        try:
            # Execute deployment sync
            success = manage_db.deploy(source_db=self.dev_db_path, target_db=self.prod_db_path, max_backups_to_keep=5)
            self.assertTrue(success)

            # 1. Verify backup was created
            backups = [f for f in os.listdir(self.backups_dir) if f.endswith('.db')]
            self.assertGreaterEqual(len(backups), 1, "At least one backup must be created before sync")

            # 2. Verify target DB has new table
            conn = sqlite3.connect(self.prod_db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()

            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='campus_announcements'")
            self.assertIsNotNone(c.fetchone(), "campus_announcements table should have been created in prod")

            # 3. Verify target DB has new column added
            c.execute("PRAGMA table_info(programs)")
            cols = [col['name'] for col in c.fetchall()]
            self.assertIn("job_placement_rate", cols, "New column job_placement_rate should be added to programs")

            # 4. Verify programs data was updated and new program inserted
            c.execute("SELECT name_en, job_placement_rate FROM programs WHERE slug='psw'")
            psw_row = c.fetchone()
            self.assertEqual(psw_row['name_en'], 'Personal Support Worker (PSW)')
            self.assertEqual(psw_row['job_placement_rate'], '95%')

            c.execute("SELECT name_en FROM programs WHERE slug='full-stack'")
            self.assertIsNotNone(c.fetchone(), "New program 'full-stack' should be inserted into prod")

            # 5. Verify live production user data is 100% preserved
            c.execute("SELECT COUNT(*) FROM users")
            self.assertEqual(c.fetchone()[0], 1)
            c.execute("SELECT email FROM users WHERE id=1")
            self.assertEqual(c.fetchone()[0], 'live@student.com')

            c.execute("SELECT COUNT(*) FROM consultations")
            self.assertEqual(c.fetchone()[0], 1)
            c.execute("SELECT email FROM consultations WHERE id=1")
            self.assertEqual(c.fetchone()[0], 'jane@test.com')

            c.execute("SELECT COUNT(*) FROM sessions")
            self.assertEqual(c.fetchone()[0], 1)
            c.execute("SELECT token FROM sessions WHERE user_id=1")
            self.assertEqual(c.fetchone()[0], 'live_token_123')

            c.execute("SELECT COUNT(*) FROM chat_logs")
            self.assertEqual(c.fetchone()[0], 1)

            # 6. Verify production secret key is PROTECTED and non-secret settings are merged
            c.execute("SELECT value FROM settings WHERE key='openai_api_key'")
            key_val = c.fetchone()[0]
            self.assertEqual(key_val, 'sk-live-prod-secret-key-12345', "Production OpenAI API key must NEVER be overwritten with blank dev seed")

            c.execute("SELECT value FROM settings WHERE key='openai_model'")
            self.assertEqual(c.fetchone()[0], 'gpt-4o', "Non-sensitive model setting should be updated")

            c.execute("SELECT value FROM settings WHERE key='enable_voice_chat'")
            self.assertEqual(c.fetchone()[0], 'true', "New setting key should be inserted")

            # 7. Verify site_translations were synced
            c.execute("SELECT text_en, text_zh FROM site_translations WHERE key='header.tagline'")
            trans = c.fetchone()
            self.assertIsNotNone(trans)
            self.assertEqual(trans['text_en'], 'Excellence in Education')

            conn.close()

        finally:
            manage_db.BACKUPS_DIR = original_backups_dir

    def test_startup_deployment_hook(self):
        """Test auto_deploy_on_startup executes once and is idempotent."""
        manage_db._DEPLOY_COMPLETED = False
        res1 = manage_db.auto_deploy_on_startup()
        self.assertTrue(res1)
        self.assertTrue(manage_db._DEPLOY_COMPLETED)

        # Second call should be instant without re-executing
        res2 = manage_db.auto_deploy_on_startup()
        self.assertTrue(res2)


if __name__ == '__main__':
    unittest.main()
