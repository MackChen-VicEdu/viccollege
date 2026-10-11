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

Whenever you edit academic programs, publish articles, update translations, or modify database schemas, you have two simple automated options:

### Option A: Fully Automated via Git Hook (Recommended)
1. Run once to install the hook on your computer:
   ```bash
   python install_git_hooks.py
   ```
2. Make your edits locally (via `/admin.html` or Python scripts).
3. Commit and push:
   ```bash
   git add .
   git commit -m "Update PSW curriculum and tuition"
   git push origin main
   ```
   *The pre-commit hook will automatically refresh the sanitized `victoria_golden_master.db` and SQL dump, stage them, and push them to Render!*

---

### Option B: Pre-Deployment CLI Helper
If you prefer explicit control before committing:
```bash
python manage_db.py prepare-deploy
git commit -am "Deploy database updates"
git push origin main
```
**What this does automatically:**
- Takes a hot, timestamped backup into `data/backups/`.
- Exports a sanitized golden snapshot to `data/seeds/victoria_golden_master.db`.
- Exports a human-readable SQL file to `data/seeds/victoria_schema_and_data_latest.sql`.
- Strips sensitive production credentials (OpenAI API keys, SMTP passwords) so they are safe for Git.
- Rebuilds dynamic sitemaps and LLM context files.

---

### What Happens on Render During Every Deployment
Render runs:
```bash
python manage_db.py deploy && gunicorn server:app --bind 0.0.0.0:$PORT
```
On every deployment boot:
1. **Automated Hot Backup**: A full, lock-safe SQLite backup of the live production database is saved to `data/backups/victoria_prod_backup_YYYYMMDD_HHMMSS.db`.
2. **Automated Pruning**: Backups are automatically rotated, retaining the 30 most recent copies to prevent disk saturation.
3. **Automated Schema Evolution**: Any newly added tables or columns (`ALTER TABLE ADD COLUMN`) from your seed are added to production.
4. **Master Content Sync**: New and updated programs, articles, job fairs, translations, and non-sensitive settings are merged into production.
5. **Zero Data Loss Guarantee**: Live consultation leads, registered users, sessions, and chat logs are **never** touched or modified.
6. **SEO & LLM Sync**: Dynamic `sitemap.xml`, `robots.txt`, and `llms.txt` are refreshed.
7. **Redundant Startup Protection**: Even if the server is started without the CLI wrapper, `server.py` invokes `manage_db.auto_deploy_on_startup()`.

---

## 3. CLI Reference: `manage_db.py`

| Command | Description | Example |
| :--- | :--- | :--- |
| `python manage_db.py deploy` | Automated deployment pipeline: hot backup, pruning, schema evolution & CMS sync | `python manage_db.py deploy` |
| `python manage_db.py prepare-deploy` | Developer pre-commit helper: updates golden master snapshot, SQL dump & sitemaps | `python manage_db.py prepare-deploy` |
| `python manage_db.py prune [N]` | Safely prunes older backups, keeping latest N copies (default: 30) | `python manage_db.py prune 30` |
| `python manage_db.py backup` | Takes a hot timestamped backup, updates golden master snapshot & SQL seed | `python manage_db.py backup` |
| `python manage_db.py sync` | Merges dev golden master into the production database (alias for deploy) | `python manage_db.py sync` |
| `python manage_db.py sync <src> <dst>` | Merges a specific source database into a target database | `python manage_db.py sync data/dev.db data/prod.db` |
| `python manage_db.py list` | Displays all available database backups with timestamps and file sizes | `python manage_db.py list` |
| `python manage_db.py restore <file>` | Safely restores database from a backup (takes a safety backup first) | `python manage_db.py restore victoria_prod_backup_20261010_202953.db` |
| `python manage_db.py dump` | Exports full schema and data to a `.sql` file with secrets sanitized | `python manage_db.py dump` |

---

## 4. How Database Sync Works

When `deploy` or `sync` executes, it performs a 5-phase safe merge:

```
[Phase 1] Pre-Deployment Safety Backup & Auto-Pruning
          Takes a hot lock-safe snapshot of live production database.
          Rotates older backups, keeping the 30 most recent files.
          ↓
[Phase 2] Schema Synchronization
          Inspects SQLite schema. Auto-adds any new tables or ALTER TABLE columns.
          ↓
[Phase 3] Master Content Merge (Selective Upsert)
          Updates programs (keyed by slug), articles, translations, Q&As, and job fairs.
          Synchronizes general settings while preserving live production API keys & secrets.
          ↓
[Phase 4] Live User Data Protection & Verification
          Verifies consultations, users, sessions, and chat logs are completely intact.
          ↓
[Phase 5] Dynamic SEO & Search Rebuild
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
    startCommand: python manage_db.py deploy && gunicorn server:app --bind 0.0.0.0:$PORT
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

### Automatic Backups
Backups are created automatically:
- Every time Render deploys or restarts (`python manage_db.py deploy`).
- Every time a database restore is attempted (`python manage_db.py restore`).
- Every time a manual backup or preparation is requested (`python manage_db.py backup` or `prepare-deploy`).

Older backups are automatically pruned to prevent disk space exhaustion (30 most recent backups kept).

### Viewing Backups
```bash
python manage_db.py list
```

### Restoring from a Backup
```bash
python manage_db.py restore victoria_prod_backup_20261010_202953.db
```
*(A safety backup of the current database is automatically created prior to restoring).*

---

## 7. Troubleshooting & FAQs

### Q1: What causes `PermissionError: [Errno 13] Permission denied: '/var/data'`?
**Answer:** On Linux containers, `/var` is owned by `root`. If a persistent disk is not mounted at `/var/data`, non-root processes cannot create directories there.  
**Resolution:** The application includes `get_safe_db_path()` which automatically checks permissions and falls back to `data/victoria.db`.

### Q2: How do I test the deployment and migration scripts locally?
Run the dedicated automated test suites:
```bash
python test_auto_deploy_db.py
python test_db_sync.py
```
This tests backup generation, backup pruning, schema migrations, master data merges, live consultation protection, and unwritable path fallbacks in an isolated sandbox.

### Q3: How do I install the Git pre-commit hook?
Run:
```bash
python install_git_hooks.py
```
Any changes to `data/victoria.db` will automatically generate fresh, sanitized seeds upon `git commit`.
