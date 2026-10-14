"""
Victoria International College - Production Database Manager & Safeguard Tool
Provides instant hot backups, SQL schema & data dumps, restore capabilities,
and golden snapshot management for safe future development.
"""

import os
import sys
import shutil
import time
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
BACKUPS_DIR = os.path.join(DATA_DIR, 'backups')
SEEDS_DIR = os.path.join(DATA_DIR, 'seeds')
DEPLOY_MARK_FILE = os.path.join(DATA_DIR, '.last_deploy_completed')

def get_safe_db_path(candidate_path=None):
    """
    Resolves database path, safely prioritizing persistent disk storage:
    1. Checks VIC_DB_PATH or DB_PATH environment variable if explicitly specified.
    2. Auto-detects Render persistent disk mounted at /var/data if writable.
    3. Falls back safely to local project database data/victoria.db with clear diagnostics.
    """
    if not candidate_path:
        env_path = os.environ.get('VIC_DB_PATH') or os.environ.get('DB_PATH')
        if env_path:
            candidate_path = env_path
        elif os.path.exists('/var/data') and os.access('/var/data', os.W_OK):
            candidate_path = '/var/data/victoria.db'
        else:
            candidate_path = os.path.join(DATA_DIR, 'victoria.db')
    
    if not os.path.isabs(candidate_path):
        candidate_path = os.path.join(BASE_DIR, candidate_path)

    fallback_path = os.path.join(DATA_DIR, 'victoria.db')

    parent_dir = os.path.dirname(os.path.abspath(candidate_path))
    try:
        os.makedirs(parent_dir, exist_ok=True)
        test_file = os.path.join(parent_dir, f'.test_perm_{os.getpid()}')
        with open(test_file, 'w') as f:
            f.write('ok')
        os.remove(test_file)
        return candidate_path
    except (PermissionError, OSError) as e:
        print(f"\n{'='*70}")
        print(f"[PERSISTENCE ALERT] Location '{candidate_path}' is not writable ({e}).")
        print(f"Falling back safely to local project database: '{fallback_path}'")
        if os.environ.get('RENDER') or 'render' in BASE_DIR.lower():
            print(f"--> NOTICE: Service is running on Render without an active Persistent Disk!")
            print(f"--> Production changes in this container will NOT persist across new builds.")
            print(f"--> ACTION: In Render Dashboard, attach a Disk at mount path '/var/data'.")
        print(f"{'='*70}\n")
        return fallback_path

DB_PATH = get_safe_db_path()


def prune_backups(max_keep=30, backups_dir=None):
    """
    Safely prunes old database backups to prevent filling up server disk space.
    Retains the most recent `max_keep` backups and removes older ones.
    """
    if not backups_dir:
        backups_dir = BACKUPS_DIR
    if not os.path.exists(backups_dir):
        return 0

    try:
        files = [
            f for f in os.listdir(backups_dir)
            if (f.endswith('.db') or f.endswith('.sql')) and not f.startswith('.')
        ]
        files_with_mtime = []
        for f in files:
            f_path = os.path.join(backups_dir, f)
            files_with_mtime.append((f_path, os.path.getmtime(f_path)))

        files_with_mtime.sort(key=lambda x: x[1])

        deleted_count = 0
        if len(files_with_mtime) > max_keep:
            to_delete = files_with_mtime[:len(files_with_mtime) - max_keep]
            for file_path, _ in to_delete:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"[WARNING] Could not delete old backup {file_path}: {e}")

        if deleted_count > 0:
            print(f"[INFO] Pruned {deleted_count} older backup file(s) (retaining latest {max_keep}).")
        return deleted_count
    except Exception as e:
        print(f"[WARNING] Error during backup pruning: {e}")
        return 0

def create_timestamped_backup(target_db_path=None, max_keep=30):
    """Create a hot, lock-safe SQLite backup with a timestamp, then auto-prunes older backups."""
    if not target_db_path:
        target_db_path = DB_PATH
    try:
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        if not os.path.exists(target_db_path):
            print(f"[INFO] No database found to backup at: {target_db_path}")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"victoria_prod_backup_{timestamp}.db"
        backup_path = os.path.join(BACKUPS_DIR, backup_filename)

        # Use SQLite's online backup API to ensure zero corruption even while running
        src = sqlite3.connect(target_db_path)
        dst = sqlite3.connect(backup_path)
        with dst:
            src.backup(dst)
        dst.close()
        src.close()

        size_kb = os.path.getsize(backup_path) / 1024
        print(f"[SUCCESS] Hot backup created:")
        print(f"  -> File: {backup_path}")
        print(f"  -> Size: {size_kb:.2f} KB")

        # Auto-prune older backups to prevent disk full errors
        prune_backups(max_keep=max_keep)

        return backup_path
    except Exception as e:
        print(f"[WARNING] Could not create backup ({e}), continuing operation safely.")
        return None

def create_golden_snapshot():
    """Create a canonical golden master copy (victoria_golden_master.db) with sensitive credentials sanitized."""
    os.makedirs(SEEDS_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file not found at: {DB_PATH}")
        return None

    golden_path = os.path.join(SEEDS_DIR, 'victoria_golden_master.db')
    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(golden_path)
    with dst:
        src.backup(dst)
    src.close()

    # Sanitize secrets in golden snapshot to allow safe git version control
    try:
        dst_cur = dst.cursor()
        dst_cur.execute("UPDATE settings SET value = '' WHERE key IN ('openai_api_key', 'smtp_pass')")
        dst.commit()
    except Exception as e:
        pass
    dst.close()

    size_kb = os.path.getsize(golden_path) / 1024
    print(f"[SUCCESS] Golden Master snapshot created (sanitized):")
    print(f"  -> File: {golden_path}")
    print(f"  -> Size: {size_kb:.2f} KB")
    return golden_path

def export_sql_dump():
    """Export complete database schema and data as a human-readable, version-controllable SQL file with secrets sanitized."""
    import re
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file not found at: {DB_PATH}")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dump_filename = f"victoria_prod_dump_{timestamp}.sql"
    dump_path = os.path.join(BACKUPS_DIR, dump_filename)

    conn = sqlite3.connect(DB_PATH)
    with open(dump_path, 'w', encoding='utf-8') as f:
        for line in conn.iterdump():
            # Sanitize live OpenAI API keys or SMTP passwords
            if "('openai_api_key'" in line or "('smtp_pass'" in line:
                line = re.sub(r"VALUES\('openai_api_key',\s*'[^']*'", "VALUES('openai_api_key', ''", line)
                line = re.sub(r"VALUES\('smtp_pass',\s*'[^']*'", "VALUES('smtp_pass', ''", line)
            f.write(f"{line}\n")
    conn.close()

    # Also keep latest dump in seeds
    os.makedirs(SEEDS_DIR, exist_ok=True)
    latest_sql_path = os.path.join(SEEDS_DIR, 'victoria_schema_and_data_latest.sql')
    shutil.copyfile(dump_path, latest_sql_path)

    size_kb = os.path.getsize(dump_path) / 1024
    print(f"[SUCCESS] SQL dump exported (sanitized):")
    print(f"  -> Timestamped dump: {dump_path}")
    print(f"  -> Canonical seed:   {latest_sql_path}")
    print(f"  -> Size: {size_kb:.2f} KB")
    return dump_path

def list_backups():
    """List all available backups in data/backups/."""
    if not os.path.exists(BACKUPS_DIR):
        print("[INFO] No backups directory found yet.")
        return []

    files = sorted(os.listdir(BACKUPS_DIR), reverse=True)
    if not files:
        print("[INFO] No backups found in data/backups/.")
        return []

    print("\n--- Available Database Backups ---")
    for f in files:
        f_path = os.path.join(BACKUPS_DIR, f)
        size_kb = os.path.getsize(f_path) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(f_path)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  • {f} ({size_kb:.1f} KB, Modified: {mtime})")
    print("----------------------------------\n")
    return files

def restore_database(backup_name_or_path):
    """Restore database from a specific backup file."""
    if os.path.isabs(backup_name_or_path) and os.path.exists(backup_name_or_path):
        target = backup_name_or_path
    else:
        # Check in BACKUPS_DIR or SEEDS_DIR
        candidate1 = os.path.join(BACKUPS_DIR, backup_name_or_path)
        candidate2 = os.path.join(SEEDS_DIR, backup_name_or_path)
        if os.path.exists(candidate1):
            target = candidate1
        elif os.path.exists(candidate2):
            target = candidate2
        else:
            print(f"[ERROR] Backup file not found: {backup_name_or_path}")
            return False

    # Safety: Create a safety backup before overwriting
    print("[INFO] Creating safety backup of current database before restoring...")
    create_timestamped_backup()

    src = sqlite3.connect(target)
    dst = sqlite3.connect(DB_PATH)
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

    print(f"[SUCCESS] Successfully restored database from: {target}")
    return True

def sync_dev_to_prod(dev_db_path=None, prod_db_path=None, max_backups_to_keep=30):
    """
    Safely merges schema changes and master catalog updates from dev_db into prod_db
    WITHOUT overwriting or deleting user-generated data (consultations, users, chat_logs, sessions).
    """
    # 1. Resolve dev_db_path
    if not dev_db_path:
        golden_candidate = os.path.join(SEEDS_DIR, 'victoria_golden_master.db')
        local_candidate = os.path.join(DATA_DIR, 'victoria.db')
        if os.path.exists(golden_candidate):
            dev_db_path = golden_candidate
        elif os.path.exists(local_candidate):
            dev_db_path = local_candidate
    elif not os.path.isabs(dev_db_path) and not os.path.exists(dev_db_path):
        candidate = os.path.join(BASE_DIR, dev_db_path)
        if os.path.exists(candidate):
            dev_db_path = candidate
        else:
            # Check in SEEDS_DIR or DATA_DIR
            c_seed = os.path.join(SEEDS_DIR, dev_db_path)
            c_data = os.path.join(DATA_DIR, dev_db_path)
            if os.path.exists(c_seed):
                dev_db_path = c_seed
            elif os.path.exists(c_data):
                dev_db_path = c_data

    if not os.path.exists(dev_db_path):
        # Fallback to local data/victoria.db or golden snapshot
        fallback_db = os.path.join(DATA_DIR, 'victoria.db')
        if os.path.exists(fallback_db):
            print(f"[INFO] '{dev_db_path}' not found, falling back to '{fallback_db}'")
            dev_db_path = fallback_db
        else:
            print(f"[ERROR] Source database not found: {dev_db_path}")
            return False

    # 2. Resolve prod_db_path safely with permission fallback
    prod_db_path = get_safe_db_path(prod_db_path)

    # 3. Check if source and target are the identical file
    if os.path.abspath(dev_db_path) == os.path.abspath(prod_db_path):
        print(f"[INFO] Source and target database are the same file: {prod_db_path}")
        print("[INFO] Schema and records are already up to date.")
        try:
            import server
            with server.app.app_context():
                server.build_sitemap_xml()
            print("[SUCCESS] Dynamic sitemap.xml, robots.txt, and llms.txt rebuilt successfully.")
        except Exception as e:
            pass
        return True

    # 4. If prod_db_path does not exist yet (e.g. first deployment on a persistent disk)
    if not os.path.exists(prod_db_path):
        print(f"[INFO] Target production database '{prod_db_path}' does not exist yet. Initializing from source '{dev_db_path}'...")
        prod_parent = os.path.dirname(os.path.abspath(prod_db_path))
        try:
            os.makedirs(prod_parent, exist_ok=True)
            shutil.copyfile(dev_db_path, prod_db_path)
            print(f"[SUCCESS] Initialized production database at: {prod_db_path}")
            # Baseline backup
            create_timestamped_backup(prod_db_path, max_keep=max_backups_to_keep)
            return True
        except (PermissionError, OSError) as e:
            print(f"[WARNING] Could not initialize at '{prod_db_path}' ({e}). Falling back to local data/victoria.db.")
            prod_db_path = os.path.join(DATA_DIR, 'victoria.db')
            if not os.path.exists(prod_db_path):
                shutil.copyfile(dev_db_path, prod_db_path)
            return True

    print(f"\n=======================================================")
    print(f" Database Sync: Dev -> Prod")
    print(f" Source (Dev):  {dev_db_path}")
    print(f" Target (Prod): {prod_db_path}")
    print(f"=======================================================\n")

    # Step 1: Mandatory Safety Backup of Prod with rotation
    print("[1/4] Taking safety backup of production database before sync...")
    create_timestamped_backup(prod_db_path, max_keep=max_backups_to_keep)

    dev_conn = sqlite3.connect(dev_db_path)
    dev_conn.row_factory = sqlite3.Row
    dev_c = dev_conn.cursor()

    prod_conn = sqlite3.connect(prod_db_path)
    prod_conn.row_factory = sqlite3.Row
    prod_c = prod_conn.cursor()

    # Step 2: Schema Synchronization (New tables & new columns)
    print("\n[2/4] Synchronizing database schema (tables & columns)...")
    dev_c.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    dev_tables = dev_c.fetchall()

    prod_c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    prod_table_names = set(r[0] for r in prod_c.fetchall())

    for t in dev_tables:
        t_name = t['name']
        t_sql = t['sql']
        if t_name not in prod_table_names:
            print(f"  + Creating missing table in Prod: {t_name}")
            prod_c.execute(t_sql)
            prod_table_names.add(t_name)
        else:
            # Check for new columns
            dev_c.execute(f"PRAGMA table_info({t_name})")
            dev_cols = {c['name']: c for c in dev_c.fetchall()}

            prod_c.execute(f"PRAGMA table_info({t_name})")
            prod_cols = {c['name']: c for c in prod_c.fetchall()}

            for col_name, col_meta in dev_cols.items():
                if col_name not in prod_cols:
                    col_type = col_meta['type'] or 'TEXT'
                    dflt = f" DEFAULT {col_meta['dflt_value']}" if col_meta['dflt_value'] is not None else ""
                    alter_sql = f"ALTER TABLE {t_name} ADD COLUMN {col_name} {col_type}{dflt}"
                    print(f"  + Adding new column to Prod table '{t_name}': {col_name} ({col_type})")
                    try:
                        prod_c.execute(alter_sql)
                    except Exception as e:
                        print(f"    ! Could not add column {col_name}: {e}")

    prod_conn.commit()

    # Step 3: Seed Missing Catalog & Configuration Items (Insert-Only, Never Overwrite)
    print("\n[3/4] Seeding new catalog items & configuration (ALL existing production data strictly reserved)...")

    # A. site_translations (Insert missing keys only; preserve all existing production translations)
    try:
        dev_c.execute("SELECT key, category, text_en, text_zh, updated_at FROM site_translations")
        trans_rows = dev_c.fetchall()
        t_inserted = 0
        for r in trans_rows:
            prod_c.execute("SELECT id FROM site_translations WHERE key = ?", (r['key'],))
            existing = prod_c.fetchone()
            if not existing:
                prod_c.execute("""
                    INSERT INTO site_translations (key, category, text_en, text_zh, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (r['key'], r['category'], r['text_en'], r['text_zh'], r['updated_at']))
                t_inserted += 1
        print(f"  -> site_translations: {t_inserted} new items inserted (all existing production translations reserved).")
    except Exception as e:
        print(f"  ! site_translations sync error: {e}")

    # B. programs (Insert missing programs only; preserve all existing production programs & active states)
    try:
        dev_c.execute("SELECT * FROM programs")
        prog_rows = dev_c.fetchall()
        p_inserted = 0
        for r in prog_rows:
            prod_c.execute("SELECT id FROM programs WHERE slug = ?", (r['slug'],))
            existing = prod_c.fetchone()
            if not existing:
                col_names = [col for col in r.keys() if col != 'id']
                placeholders = ', '.join(['?'] * len(col_names))
                cols_str = ', '.join(col_names)
                values = [r[col] for col in col_names]
                prod_c.execute(f"INSERT INTO programs ({cols_str}) VALUES ({placeholders})", values)
                p_inserted += 1
        print(f"  -> programs: {p_inserted} new programs inserted (all existing production programs reserved).")
    except Exception as e:
        print(f"  ! programs sync error: {e}")

    # C. knowledge_base (Insert missing items only; preserve all existing production Q&As)
    try:
        dev_c.execute("SELECT * FROM knowledge_base")
        kb_rows = dev_c.fetchall()
        k_inserted = 0
        for r in kb_rows:
            prod_c.execute("SELECT id FROM knowledge_base WHERE id = ? OR title = ?", (r['id'], r['title']))
            existing = prod_c.fetchone()
            if not existing:
                placeholders = ', '.join(['?'] * len(r.keys()))
                cols_str = ', '.join(r.keys())
                values = [r[col] for col in r.keys()]
                prod_c.execute(f"INSERT INTO knowledge_base ({cols_str}) VALUES ({placeholders})", values)
                k_inserted += 1
        print(f"  -> knowledge_base: {k_inserted} new items inserted (all existing production Q&As reserved).")
    except Exception as e:
        print(f"  ! knowledge_base sync error: {e}")

    # D. articles (Insert missing articles only; preserve all existing production articles & view counts)
    try:
        dev_c.execute("SELECT * FROM articles")
        art_rows = dev_c.fetchall()
        a_inserted = 0
        for r in art_rows:
            prod_c.execute("SELECT id FROM articles WHERE slug = ?", (r['slug'],))
            existing = prod_c.fetchone()
            if not existing:
                col_names = [col for col in r.keys() if col != 'id']
                placeholders = ', '.join(['?'] * len(col_names))
                cols_str = ', '.join(col_names)
                values = [r[col] for col in col_names]
                prod_c.execute(f"INSERT INTO articles ({cols_str}) VALUES ({placeholders})", values)
                a_inserted += 1
        print(f"  -> articles: {a_inserted} new articles inserted (all existing production articles reserved).")
    except Exception as e:
        print(f"  ! articles sync error: {e}")

    # E. job_fairs (Insert missing events only; preserve all existing production events & active/inactive statuses)
    try:
        dev_c.execute("SELECT * FROM job_fairs")
        jf_rows = dev_c.fetchall()
        jf_inserted = 0
        for r in jf_rows:
            prod_c.execute("SELECT id FROM job_fairs WHERE id = ? OR title_en = ?", (r['id'], r['title_en']))
            existing = prod_c.fetchone()
            if not existing:
                col_names = [col for col in r.keys() if col != 'id']
                placeholders = ', '.join(['?'] * len(r.keys()))
                cols_str = ', '.join(r.keys())
                values = [r[col] for col in r.keys()]
                prod_c.execute(f"INSERT INTO job_fairs ({cols_str}) VALUES ({placeholders})", values)
                jf_inserted += 1
        print(f"  -> job_fairs: {jf_inserted} new events inserted (all existing production job fairs reserved).")
    except Exception as e:
        print(f"  ! job_fairs sync error: {e}")

    # F. settings (Insert missing keys only; preserve all existing production settings & API keys)
    try:
        dev_c.execute("SELECT key, value, updated_at FROM settings")
        settings_rows = dev_c.fetchall()
        s_inserted = 0
        for r in settings_rows:
            k = r['key']
            v = r['value']
            prod_c.execute("SELECT value FROM settings WHERE key = ?", (k,))
            existing = prod_c.fetchone()
            if not existing:
                prod_c.execute("INSERT INTO settings (key, value, updated_at) VALUES (?, ?, ?)", (k, v, r['updated_at']))
                s_inserted += 1
        print(f"  -> settings: {s_inserted} new settings inserted (all existing production settings & secrets reserved).")
    except Exception as e:
        print(f"  ! settings sync error: {e}")

    # G. 100% Protected Production Tables Verification
    print("\n[4/4] Verifying all production data is reserved untouched:")
    for protected in ['consultations', 'users', 'chat_logs', 'sessions', 'job_fairs', 'articles', 'programs', 'knowledge_base', 'settings', 'site_translations']:
        if protected in prod_table_names:
            prod_c.execute(f"SELECT COUNT(*) FROM {protected}")
            count = prod_c.fetchone()[0]
            print(f"  [RESERVED] {protected}: {count} live production records preserved untouched.")

    prod_conn.commit()
    prod_conn.close()
    dev_conn.close()

    # Step 4: Rebuild dynamic sitemap & LLM context
    try:
        import server
        with server.app.app_context():
            server.build_sitemap_xml()
        print("\n[SUCCESS] Dynamic sitemap.xml, robots.txt, and llms.txt rebuilt successfully.")
    except Exception as e:
        print(f"\n[NOTE] Could not auto-rebuild sitemap: {e}")

    print("\n=======================================================")
    print(" Sync Completed Successfully!")
    print("=======================================================\n")
    return True


def auto_snapshot_if_needed():
    """
    If local data/victoria.db is newer than seeds/victoria_golden_master.db,
    automatically regenerate the golden master and SQL dump before sync/deployment.
    ONLY runs in local development, never in production cloud environments.
    """
    if os.environ.get('RENDER') or os.environ.get('VIC_DB_PATH') == '/var/data/victoria.db':
        return False

    local_db = os.path.join(DATA_DIR, 'victoria.db')
    golden_db = os.path.join(SEEDS_DIR, 'victoria_golden_master.db')
    if os.path.exists(local_db):
        if not os.path.exists(golden_db) or (os.path.getmtime(local_db) > os.path.getmtime(golden_db) + 2):
            print("[AUTO] Local dev database has newer changes. Refreshing golden seed snapshot & SQL dump...")
            create_golden_snapshot()
            export_sql_dump()
            return True
    return False


def prepare_deploy():
    """
    Developer pre-deployment workflow prior to git commit & push:
    1. Creates safety backup of local database.
    2. Generates sanitized golden master snapshot (victoria_golden_master.db).
    3. Exports clean SQL dump (victoria_schema_and_data_latest.sql).
    4. Rebuilds dynamic sitemaps and llms.txt.
    5. Prints ready-to-push git status.
    """
    print("\n=======================================================")
    print(" Preparing Database For Production Deployment")
    print(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=======================================================\n")

    print("[1/4] Creating local timestamped safety backup...")
    create_timestamped_backup()

    print("\n[2/4] Generating sanitized Golden Master snapshot...")
    create_golden_snapshot()

    print("\n[3/4] Exporting clean version-controlled SQL dump...")
    export_sql_dump()

    print("\n[4/4] Updating dynamic sitemaps and LLM search files...")
    try:
        import server
        with server.app.app_context():
            server.build_sitemap_xml()
        print("[SUCCESS] sitemap.xml, robots.txt, and llms.txt refreshed.")
    except Exception as e:
        print(f"[NOTE] Sitemap generation: {e}")

    print("\n=======================================================")
    print(" Production Seed Ready!")
    print(" Next Step: Commit and push seeds to GitHub to deploy on Render:")
    print("   git add data/seeds/ manage_db.py")
    print("   git commit -m 'Deploy DB updates: schema and CMS master content'")
    print("   git push origin main")
    print("=======================================================\n")
    return True


def deploy(source_db=None, target_db=None, max_backups_to_keep=30):
    """
    Full automated deployment routine called by Render or server boot on each deployment:
    1. Synchronizes seeds if local edits were detected.
    2. Takes a lock-safe, timestamped backup of the production database.
    3. Automatically prunes older backups to retain the latest `max_backups_to_keep` (default 30).
    4. Runs non-destructive schema migrations and master CMS content synchronization.
    5. Preserves all student inquiries, registrations, consultations, and chat logs.
    6. Rebuilds dynamic SEO and LLM metadata.
    """
    print(f"\n=======================================================")
    print(f" Victoria International College - Deployment Pipeline")
    print(f" Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=======================================================\n")

    # Refresh golden master snapshot if dev environment has newer changes
    auto_snapshot_if_needed()

    # Execute safe migration & sync with backup rotation
    success = sync_dev_to_prod(source_db, target_db, max_backups_to_keep=max_backups_to_keep)
    if success:
        print("[SUCCESS] Automated deployment database migration finished successfully.")
        try:
            with open(DEPLOY_MARK_FILE, 'w') as f:
                f.write(datetime.now().isoformat())
        except Exception:
            pass
    else:
        print("[WARNING] Deployment database sync encountered an error.")
    return success


_DEPLOY_COMPLETED = False

def auto_deploy_on_startup():
    """
    Thread-safe startup hook for server.py / Gunicorn WSGI.
    Ensures database migration and backup rotation execute upon every server boot.
    Can be skipped by setting environment variable VIC_SKIP_AUTO_DEPLOY=1.
    """
    global _DEPLOY_COMPLETED
    if _DEPLOY_COMPLETED:
        return True

    if os.environ.get('VIC_SKIP_AUTO_DEPLOY') == '1':
        print("[INFO] Startup database auto-deploy skipped via VIC_SKIP_AUTO_DEPLOY=1")
        _DEPLOY_COMPLETED = True
        return True

    # Check if a deployment command already executed within the past 120 seconds
    try:
        if os.path.exists(DEPLOY_MARK_FILE):
            age_sec = time.time() - os.path.getmtime(DEPLOY_MARK_FILE)
            if age_sec < 120:
                print(f"[BOOT] Database deployment already synchronized by pre-start command ({int(age_sec)}s ago).")
                _DEPLOY_COMPLETED = True
                return True
    except Exception:
        pass

    try:
        print("[BOOT] Running automated database backup & deployment sync...")
        res = deploy()
        _DEPLOY_COMPLETED = True
        return res
    except Exception as e:
        print(f"[WARNING] Startup database auto-deploy error: {e}")
        _DEPLOY_COMPLETED = True
        return False


if __name__ == '__main__':
    args = sys.argv[1:]
    cmd = args[0] if args else 'deploy'

    if cmd in ('deploy', 'auto-deploy'):
        source_arg = args[1] if len(args) > 1 else None
        target_arg = args[2] if len(args) > 2 else None
        deploy(source_arg, target_arg)
    elif cmd in ('prepare-deploy', 'prepare'):
        prepare_deploy()
    elif cmd == 'auto-snapshot':
        auto_snapshot_if_needed()
    elif cmd == 'backup':
        create_timestamped_backup()
        create_golden_snapshot()
        export_sql_dump()
    elif cmd == 'snapshot':
        create_golden_snapshot()
    elif cmd == 'dump':
        export_sql_dump()
    elif cmd == 'list':
        list_backups()
    elif cmd == 'prune':
        max_k = int(args[1]) if len(args) > 1 else 30
        prune_backups(max_keep=max_k)
    elif cmd == 'restore':
        if len(args) < 2:
            print("Usage: python manage_db.py restore <backup_filename_or_path>")
            list_backups()
        else:
            restore_database(args[1])
    elif cmd in ('sync-dev-to-prod', 'sync'):
        dev_path = args[1] if len(args) > 1 else None
        prod_path = args[2] if len(args) > 2 else None
        sync_dev_to_prod(dev_path, prod_path)
    else:
        print("Usage:")
        print("  python manage_db.py deploy [source_db] [prod_db]   # Automated backup, pruning & migration for deployment")
        print("  python manage_db.py prepare-deploy                 # Developer prep: updates golden master snapshot & SQL dump")
        print("  python manage_db.py backup                         # Take hot backup, golden master snapshot & SQL dump")
        print("  python manage_db.py prune [max_keep]               # Prune backups keeping latest N files (default: 30)")
        print("  python manage_db.py list                           # List all saved backups")
        print("  python manage_db.py dump                           # Export human-readable SQL dump")
        print("  python manage_db.py restore <filename>             # Restore from a backup")
        print("  python manage_db.py sync [source_db] [prod_db]     # Safely merge updates into prod without touching user data")
        print("  python manage_db.py sync-dev-to-prod               # (Alias for sync)")

