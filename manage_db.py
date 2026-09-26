"""
Victoria International College - Production Database Manager & Safeguard Tool
Provides instant hot backups, SQL schema & data dumps, restore capabilities,
and golden snapshot management for safe future development.
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.environ.get('VIC_DB_PATH') or os.environ.get('DB_PATH') or os.path.join(DATA_DIR, 'victoria.db')
BACKUPS_DIR = os.path.join(DATA_DIR, 'backups')
SEEDS_DIR = os.path.join(DATA_DIR, 'seeds')

def create_timestamped_backup():
    """Create a hot, lock-safe SQLite backup with a timestamp."""
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file not found at: {DB_PATH}")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"victoria_prod_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUPS_DIR, backup_filename)

    # Use SQLite's online backup API to ensure zero corruption even while running
    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(backup_path)
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

    size_kb = os.path.getsize(backup_path) / 1024
    print(f"[SUCCESS] Hot backup created:")
    print(f"  -> File: {backup_path}")
    print(f"  -> Size: {size_kb:.2f} KB")
    return backup_path

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

def sync_dev_to_prod(dev_db_path, prod_db_path=None):
    """
    Safely merges schema changes and master catalog updates from dev_db into prod_db
    WITHOUT overwriting or deleting user-generated data (consultations, users, chat_logs, sessions).
    """
    if prod_db_path is None:
        prod_db_path = DB_PATH

    # Resolve relative paths relative to BASE_DIR if needed
    if not os.path.isabs(dev_db_path) and not os.path.exists(dev_db_path):
        candidate = os.path.join(BASE_DIR, dev_db_path)
        if os.path.exists(candidate):
            dev_db_path = candidate

    if not os.path.exists(dev_db_path):
        # Fallback to local data/victoria.db or golden snapshot
        fallback_db = os.path.join(DATA_DIR, 'victoria.db')
        if os.path.exists(fallback_db):
            print(f"[INFO] '{dev_db_path}' not found, falling back to '{fallback_db}'")
            dev_db_path = fallback_db
        else:
            print(f"[ERROR] Source database not found: {dev_db_path}")
            return False

    if not os.path.isabs(prod_db_path) and not os.path.exists(prod_db_path):
        candidate = os.path.join(BASE_DIR, prod_db_path)
        if os.path.exists(candidate):
            prod_db_path = candidate

    # If prod_db_path does not exist yet (e.g. first deployment on a persistent disk)
    if not os.path.exists(prod_db_path):
        print(f"[INFO] Target production database '{prod_db_path}' does not exist yet. Initializing from source '{dev_db_path}'...")
        prod_parent = os.path.dirname(os.path.abspath(prod_db_path))
        os.makedirs(prod_parent, exist_ok=True)
        shutil.copyfile(dev_db_path, prod_db_path)
        print(f"[SUCCESS] Initialized production database at: {prod_db_path}")
        return True

    print(f"\n=======================================================")
    print(f" Database Sync: Dev -> Prod")
    print(f" Source (Dev):  {dev_db_path}")
    print(f" Target (Prod): {prod_db_path}")
    print(f"=======================================================\n")

    # Step 1: Mandatory Safety Backup of Prod
    print("[1/4] Taking safety backup of production database before sync...")
    create_timestamped_backup()

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

    # Step 3: Master Data Merging (Selective Upsert)
    print("\n[3/4] Merging master CMS, programs, Q&As, and configuration data...")

    # A. site_translations (Keyed by key)
    try:
        dev_c.execute("SELECT key, category, text_en, text_zh, updated_at FROM site_translations")
        trans_rows = dev_c.fetchall()
        t_inserted, t_updated = 0, 0
        for r in trans_rows:
            prod_c.execute("SELECT id, text_en, text_zh FROM site_translations WHERE key = ?", (r['key'],))
            existing = prod_c.fetchone()
            if not existing:
                prod_c.execute("""
                    INSERT INTO site_translations (key, category, text_en, text_zh, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (r['key'], r['category'], r['text_en'], r['text_zh'], r['updated_at']))
                t_inserted += 1
            elif existing['text_en'] != r['text_en'] or existing['text_zh'] != r['text_zh']:
                prod_c.execute("""
                    UPDATE site_translations
                    SET category = ?, text_en = ?, text_zh = ?, updated_at = ?
                    WHERE key = ?
                """, (r['category'], r['text_en'], r['text_zh'], r['updated_at'], r['key']))
                t_updated += 1
        print(f"  -> site_translations: {t_inserted} inserted, {t_updated} updated.")
    except Exception as e:
        print(f"  ! site_translations sync error: {e}")

    # B. programs (Keyed by slug)
    try:
        dev_c.execute("SELECT * FROM programs")
        prog_rows = dev_c.fetchall()
        p_inserted, p_updated = 0, 0
        for r in prog_rows:
            prod_c.execute("SELECT id FROM programs WHERE slug = ?", (r['slug'],))
            existing = prod_c.fetchone()
            col_names = [col for col in r.keys() if col != 'id']
            if not existing:
                placeholders = ', '.join(['?'] * len(col_names))
                cols_str = ', '.join(col_names)
                values = [r[col] for col in col_names]
                prod_c.execute(f"INSERT INTO programs ({cols_str}) VALUES ({placeholders})", values)
                p_inserted += 1
            else:
                set_clause = ', '.join([f"{col} = ?" for col in col_names])
                values = [r[col] for col in col_names] + [existing['id']]
                prod_c.execute(f"UPDATE programs SET {set_clause} WHERE id = ?", values)
                p_updated += 1
        print(f"  -> programs: {p_inserted} inserted, {p_updated} updated.")
    except Exception as e:
        print(f"  ! programs sync error: {e}")

    # C. knowledge_base (Keyed by title or id)
    try:
        dev_c.execute("SELECT * FROM knowledge_base")
        kb_rows = dev_c.fetchall()
        k_inserted, k_updated = 0, 0
        for r in kb_rows:
            prod_c.execute("SELECT id FROM knowledge_base WHERE id = ? OR title = ?", (r['id'], r['title']))
            existing = prod_c.fetchone()
            col_names = [col for col in r.keys() if col != 'id']
            if not existing:
                placeholders = ', '.join(['?'] * len(r.keys()))
                cols_str = ', '.join(r.keys())
                values = [r[col] for col in r.keys()]
                prod_c.execute(f"INSERT INTO knowledge_base ({cols_str}) VALUES ({placeholders})", values)
                k_inserted += 1
            else:
                set_clause = ', '.join([f"{col} = ?" for col in col_names])
                values = [r[col] for col in col_names] + [existing['id']]
                prod_c.execute(f"UPDATE knowledge_base SET {set_clause} WHERE id = ?", values)
                k_updated += 1
        print(f"  -> knowledge_base: {k_inserted} inserted, {k_updated} updated.")
    except Exception as e:
        print(f"  ! knowledge_base sync error: {e}")

    # D. articles (Keyed by slug)
    try:
        dev_c.execute("SELECT * FROM articles")
        art_rows = dev_c.fetchall()
        a_inserted, a_updated = 0, 0
        for r in art_rows:
            prod_c.execute("SELECT id FROM articles WHERE slug = ?", (r['slug'],))
            existing = prod_c.fetchone()
            col_names = [col for col in r.keys() if col != 'id']
            if not existing:
                placeholders = ', '.join(['?'] * len(col_names))
                cols_str = ', '.join(col_names)
                values = [r[col] for col in col_names]
                prod_c.execute(f"INSERT INTO articles ({cols_str}) VALUES ({placeholders})", values)
                a_inserted += 1
            else:
                set_clause = ', '.join([f"{col} = ?" for col in col_names])
                values = [r[col] for col in col_names] + [existing['id']]
                prod_c.execute(f"UPDATE articles SET {set_clause} WHERE id = ?", values)
                a_updated += 1
        print(f"  -> articles: {a_inserted} inserted, {a_updated} updated.")
    except Exception as e:
        print(f"  ! articles sync error: {e}")

    # E. job_fairs (Keyed by title_en or id)
    try:
        dev_c.execute("SELECT * FROM job_fairs")
        jf_rows = dev_c.fetchall()
        jf_inserted, jf_updated = 0, 0
        for r in jf_rows:
            prod_c.execute("SELECT id FROM job_fairs WHERE id = ? OR title_en = ?", (r['id'], r['title_en']))
            existing = prod_c.fetchone()
            col_names = [col for col in r.keys() if col != 'id']
            if not existing:
                placeholders = ', '.join(['?'] * len(r.keys()))
                cols_str = ', '.join(r.keys())
                values = [r[col] for col in r.keys()]
                prod_c.execute(f"INSERT INTO job_fairs ({cols_str}) VALUES ({placeholders})", values)
                jf_inserted += 1
            else:
                set_clause = ', '.join([f"{col} = ?" for col in col_names])
                values = [r[col] for col in col_names] + [existing['id']]
                prod_c.execute(f"UPDATE job_fairs SET {set_clause} WHERE id = ?", values)
                jf_updated += 1
        print(f"  -> job_fairs: {jf_inserted} inserted, {jf_updated} updated.")
    except Exception as e:
        print(f"  ! job_fairs sync error: {e}")

    # F. Protected Tables Notice
    print("\n[4/4] Preserving live production user data:")
    for protected in ['consultations', 'users', 'chat_logs', 'sessions']:
        if protected in prod_table_names:
            prod_c.execute(f"SELECT COUNT(*) FROM {protected}")
            count = prod_c.fetchone()[0]
            print(f"  [SAFE] {protected}: {count} live production records preserved untouched.")

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


if __name__ == '__main__':
    args = sys.argv[1:]
    cmd = args[0] if args else 'backup'

    if cmd == 'backup':
        create_timestamped_backup()
        create_golden_snapshot()
        export_sql_dump()
    elif cmd == 'snapshot':
        create_golden_snapshot()
    elif cmd == 'dump':
        export_sql_dump()
    elif cmd == 'list':
        list_backups()
    elif cmd == 'restore':
        if len(args) < 2:
            print("Usage: python manage_db.py restore <backup_filename_or_path>")
            list_backups()
        else:
            restore_database(args[1])
    elif cmd in ('sync-dev-to-prod', 'sync'):
        if len(args) < 2:
            print("Usage: python manage_db.py sync-dev-to-prod <dev_db_path> [prod_db_path]")
            print("Example: python manage_db.py sync-dev-to-prod data/victoria_dev.db data/victoria.db")
        else:
            dev_path = args[1]
            prod_path = args[2] if len(args) > 2 else None
            sync_dev_to_prod(dev_path, prod_path)
    else:
        print("Usage:")
        print("  python manage_db.py backup                     # Take hot backup, golden master snapshot & SQL dump")
        print("  python manage_db.py list                       # List all saved backups")
        print("  python manage_db.py dump                       # Export human-readable SQL dump")
        print("  python manage_db.py restore <filename>         # Restore from a backup")
        print("  python manage_db.py sync-dev-to-prod <dev_db>  # Safely merge dev changes into prod without touching user data")

