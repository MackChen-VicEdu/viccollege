"""
Automated unit & integration test for safe Dev-to-Prod Database Sync.
Verifies that schema migrations and master catalog updates are merged
WITHOUT overwriting or losing live production user data (consultations, users, logs).
"""
import unittest
import os
import sqlite3
import shutil
import manage_db

class TestDatabaseDevToProdSync(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), 'scratch', 'test_sync_sandbox')
        os.makedirs(self.test_dir, exist_ok=True)
        self.prod_db = os.path.join(self.test_dir, 'prod.db')
        self.dev_db = os.path.join(self.test_dir, 'dev.db')

        # Copy current production database to sandbox prod.db and dev.db
        shutil.copyfile(manage_db.DB_PATH, self.prod_db)
        shutil.copyfile(manage_db.DB_PATH, self.dev_db)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_sync_preserves_user_data_and_merges_dev_changes(self):
        # 1. Simulate live production user activity (new consultation lead submitted in PROD)
        prod_conn = sqlite3.connect(self.prod_db)
        prod_c = prod_conn.cursor()
        prod_c.execute("""
            INSERT INTO consultations (name, email, phone, program, notes, status, created_at)
            VALUES ('Live Student in Prod', 'live_student@prod.com', '416-555-9999', 'psw', 'Urgent grant inquiry', 'new', '2026-09-25T23:00:00')
        """)
        prod_conn.commit()
        prod_conn.close()

        # 2. Simulate developer changes in DEV:
        #    a) New Table in Dev: 'scholarships'
        #    b) New Column in Dev: programs.career_outcomes_en
        #    c) Updated program title in Dev
        #    d) New site translation key in Dev
        dev_conn = sqlite3.connect(self.dev_db)
        dev_c = dev_conn.cursor()
        dev_c.execute("""
            CREATE TABLE scholarships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount INTEGER NOT NULL
            )
        """)
        dev_c.execute("INSERT INTO scholarships (name, amount) VALUES ('President Entrance Scholarship', 3000)")

        dev_c.execute("ALTER TABLE programs ADD COLUMN career_outcomes_en TEXT DEFAULT ''")
        dev_c.execute("UPDATE programs SET career_outcomes_en = 'High-Demand Hospital Roles' WHERE slug = 'psw'")

        dev_c.execute("""
            INSERT INTO site_translations (key, category, text_en, text_zh, updated_at)
            VALUES ('test_new_dev_key', 'general', 'New Feature Available', '新功能上线', '2026-09-25T23:00:00')
        """)
        dev_conn.commit()
        dev_conn.close()

        # 3. Execute sync_dev_to_prod
        success = manage_db.sync_dev_to_prod(self.dev_db, self.prod_db)
        self.assertTrue(success, "sync_dev_to_prod must succeed")

        # 4. Verify PROD Database State:
        prod_check = sqlite3.connect(self.prod_db)
        prod_check.row_factory = sqlite3.Row
        cur = prod_check.cursor()

        # Check A: Live Prod user consultation lead is 100% PRESERVED!
        cur.execute("SELECT * FROM consultations WHERE email = 'live_student@prod.com'")
        lead = cur.fetchone()
        self.assertIsNotNone(lead, "Live production consultation data must NOT be lost during sync!")
        self.assertEqual(lead['name'], 'Live Student in Prod')

        # Check B: New Table 'scholarships' migrated to Prod
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scholarships'")
        self.assertIsNotNone(cur.fetchone(), "New table 'scholarships' must be created in Prod")

        # Check C: New Column 'career_outcomes_en' added to Prod programs
        cur.execute("SELECT career_outcomes_en FROM programs WHERE slug = 'psw'")
        psw_row = cur.fetchone()
        self.assertEqual(psw_row['career_outcomes_en'], 'High-Demand Hospital Roles')

        # Check D: New Translation key migrated to Prod
        cur.execute("SELECT text_en, text_zh FROM site_translations WHERE key = 'test_new_dev_key'")
        trans_row = cur.fetchone()
        self.assertIsNotNone(trans_row)
        self.assertEqual(trans_row['text_en'], 'New Feature Available')

        prod_check.close()

if __name__ == '__main__':
    unittest.main()
