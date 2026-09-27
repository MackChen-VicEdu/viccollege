# Victoria International College — Database Management & Deployment Guide

This guide explains how to develop locally, manage database backups, and safely sync changes to production without losing live user data (such as student consultation inquiries, registered users, and chat logs).

---

## Table of Contents
1. [Core Principles & Data Architecture](#1-core-principles--data-architecture)
2. [Step-by-Step Workflow: Updating Production](#2-step-by-step-workflow-updating-production)
3. [CLI Reference: `manage_db.py`](#3-cli-reference-manage_dbpy)
4. [How Database Sync Works](#4-how-database-sync-works)
5. [Render & Production Setup](#5-render--production-setup)
6. [Backups & Disaster Recovery](#6-backups--disaster-recovery)
7. [Troubleshooting & FAQs](#7-troubleshooting--faqs)

---

## 1. Core Principles & Data Architecture

The Victoria College database (`victoria.db`) contains two distinct categories of data:

| Category | Tables | Handled By | Sync Behavior |
| :--- | :--- | :--- | :--- |
| **Master Content & Schema** | `programs`, `articles`, `job_fairs`, `knowledge_base`, `site_translations`, `settings` | Developer / Admin | **Merged & Updated** from Dev to Prod |
| **Live User Submissions** | `consultations`, `users`, `chat_logs`, `sessions` | Real Website Visitors | **100% Protected & Preserved** (Never Overwritten) |

> [!IMPORTANT]
> Live student leads submitted on the live website will **never** be deleted or overwritten when you deploy updates from your local dev environment.

---

## 2. Step-by-Step Workflow: Updating Production

Whenever you edit academic programs, publish articles, update translations, or modify database schemas, follow these 3 steps:

### Step 1: Make Changes Locally in Dev
1. Start your local server:
   ```bash
   python server.py
   ```
2. Make your edits via the Admin Portal (`/admin.html`) or through migration scripts.
3. Verify your changes in your browser (`http://localhost:5055`).

---

### Step 2: Create a Snapshot & Seed
Before committing, run the backup command in your terminal:
```bash
python manage_db.py backup
```
**What this does automatically:**
- Takes a hot, timestamped backup into `data/backups/`.
- Exports a sanitized golden snapshot to `data/seeds/victoria_golden_master.db`.
- Exports a human-readable SQL file to `data/seeds/victoria_schema_and_data_latest.sql`.
- Strips sensitive production credentials (OpenAI API keys, SMTP passwords) so they are safe for Git.

---

### Step 3: Commit and Push to GitHub
```bash
git add .
git commit -m "Update programs catalog and add new blog article"
git push origin main
```

---

### Step 4: Automatic Deployment on Render
Render detects the new commit on `main` and automatically:
1. Installs Python dependencies (`pip install -r requirements.txt`).
2. Runs:
   ```bash
   python manage_db.py sync
   ```
3. Starts the production server with Gunicorn.

**During Step 2 of the startup, the sync engine:**
- Adds any newly created tables or columns to the production database.
- Updates programs, articles, and content from the golden master.
- Preserves all live consultation leads and registered users.
- Automatically regenerates `sitemap.xml`, `robots.txt`, and `llms.txt`.

---

## 3. CLI Reference: `manage_db.py`

| Command | Description | Example |
| :--- | :--- | :--- |
| `python manage_db.py backup` | Takes a hot timestamped backup, updates golden master snapshot & SQL seed | `python manage_db.py backup` |
| `python manage_db.py sync` | Merges dev golden master into the production database | `python manage_db.py sync` |
| `python manage_db.py sync <src> <dst>` | Merges a specific source database into a target database | `python manage_db.py sync data/dev.db data/prod.db` |
| `python manage_db.py list` | Displays all available database backups with timestamps and file sizes | `python manage_db.py list` |
| `python manage_db.py restore <file>` | Safely restores database from a backup (takes a safety backup first) | `python manage_db.py restore victoria_prod_backup_20260927_000944.db` |
| `python manage_db.py dump` | Exports full schema and data to a `.sql` file | `python manage_db.py dump` |

---

## 4. How Database Sync Works

When `sync` executes, it performs a 4-phase safe merge:

```
[Phase 1] Pre-Sync Safety Backup
          Takes an automatic snapshot of production before touching anything.
          ↓
[Phase 2] Schema Migration
          Inspects SQLite schema. Auto-adds any new tables or ALTER TABLE columns.
          ↓
[Phase 3] Master Content Merge (Selective Upsert)
          Updates programs (keyed by slug), articles, translations, and Q&As.
          ↓
[Phase 4] Live User Data Protection & Verification
          Verifies consultations, users, and logs are completely intact.
          ↓
[Phase 5] Dynamic SEO Rebuild
          Re-indexes sitemap.xml, robots.txt, and llms.txt with fresh URLs.
```

---

## 5. Render & Production Setup

### Configuration (`render.yaml`)
```yaml
services:
  - type: web
    name: viccollege-platform
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python manage_db.py sync && gunicorn server:app --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.8
      - key: VIC_DB_PATH
        value: /var/data/victoria.db
    disk:
      name: viccollege-data
      mountPath: /var/data
      sizeGB: 1
```

### Self-Healing Database Path Resolution
- **With Persistent Disk**: If a persistent disk is mounted at `/var/data`, the database resides in `/var/data/victoria.db` and persists across redeployments.
- **Without Persistent Disk / Free Tier**: If `/var/data` is not writable, the system automatically detects this and falls back to `data/victoria.db` without crashing or throwing `PermissionError: [Errno 13]`.

---

## 6. Backups & Disaster Recovery

### Creating a Manual Backup
To create a backup at any time:
```bash
python manage_db.py backup
```

### Viewing Backups
```bash
python manage_db.py list
```
Output:
```text
--- Available Database Backups ---
  • victoria_prod_backup_20260927_000944.db (1320.0 KB, Modified: 2026-09-27 00:09:44)
  • victoria_prod_backup_20260925_183012.db (1305.2 KB, Modified: 2026-09-25 18:30:12)
----------------------------------
```

### Restoring from a Backup
```bash
python manage_db.py restore victoria_prod_backup_20260927_000944.db
```
*(A safety backup of the current database is automatically created prior to restoring).*

---

## 7. Troubleshooting & FAQs

### Q1: What causes `PermissionError: [Errno 13] Permission denied: '/var/data'`?
**Answer:** On Linux containers, `/var` is owned by `root`. If a persistent disk is not mounted at `/var/data`, non-root processes cannot create directories there.  
**Resolution:** The application includes `get_safe_db_path()` which automatically checks permissions and falls back to `data/victoria.db`.

### Q2: How do I test the sync script locally?
Run the dedicated automated test suite:
```bash
python -m unittest test_db_sync.py
```
This tests schema migrations, master data merges, live consultation protection, and unwritable path fallbacks in an isolated sandbox.

### Q3: How do I run tests for the full platform?
```bash
python -m unittest discover -s . -p "test_*.py"
```
All 87 tests will run and verify API endpoints, database integrity, email integrations, and SEO generators.
