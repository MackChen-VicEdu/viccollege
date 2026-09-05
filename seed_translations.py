import sqlite3
import os
import re
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'victoria.db')
TRANSLATIONS_JS = os.path.join(BASE_DIR, 'js', 'translations.js')

def extract_translations_from_js():
    with open(TRANSLATIONS_JS, 'r', encoding='utf-8') as f:
        content = f.read()

    en_dict = {}
    zh_dict = {}

    en_match = re.search(r'en:\s*\{(.*?)\n\s*\},?\s*zh:', content, re.DOTALL)
    zh_match = re.search(r'zh:\s*\{(.*?)\n\s*\}\s*\};', content, re.DOTALL)

    if not en_match or not zh_match:
        print("Regex failed to find en and zh blocks")
        return {}, {}

    en_text = en_match.group(1)
    zh_text = zh_match.group(1)

    line_pattern = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*:\s*("(?:\\.|[^"\\])*"|`[\s\S]*?`)\s*,?\s*$', re.MULTILINE)

    for m in line_pattern.finditer(en_text):
        k = m.group(1)
        v = m.group(2)
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1].replace('\\"', '"').replace('\\n', '\n')
        elif v.startswith('`') and v.endswith('`'):
            v = v[1:-1]
        en_dict[k] = v

    for m in line_pattern.finditer(zh_text):
        k = m.group(1)
        v = m.group(2)
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1].replace('\\"', '"').replace('\\n', '\n')
        elif v.startswith('`') and v.endswith('`'):
            v = v[1:-1]
        zh_dict[k] = v

    return en_dict, zh_dict

def seed_database():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS site_translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        category TEXT DEFAULT 'general',
        text_en TEXT NOT NULL,
        text_zh TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''')

    en_dict, zh_dict = extract_translations_from_js()
    all_keys = sorted(set(list(en_dict.keys()) + list(zh_dict.keys())))
    now_str = datetime.utcnow().isoformat()

    inserted = 0
    updated = 0

    for k in all_keys:
        text_en = en_dict.get(k, '')
        text_zh = zh_dict.get(k, '')

        category = 'general'
        if k.startswith('topbar_') or k.startswith('logo_'):
            category = 'header'
        elif k.startswith('nav_'):
            category = 'navigation'
        elif k.startswith('hero_') or k.startswith('cat_'):
            category = 'hero'
        elif k.startswith('banner_'):
            category = 'banner'
        elif k.startswith('why_'):
            category = 'value_props'
        elif k.startswith('prog_') or k.startswith('tab_'):
            category = 'programs'
        elif k.startswith('aid_'):
            category = 'financial_aid'
        elif k.startswith('lead_'):
            category = 'leadership'
        elif k.startswith('test_'):
            category = 'testimonials'
        elif k.startswith('form_'):
            category = 'consultation'
        elif k.startswith('campus_'):
            category = 'campuses'
        elif k.startswith('footer_'):
            category = 'footer'

        cursor.execute("SELECT id FROM site_translations WHERE key = ?", (k,))
        row = cursor.fetchone()
        if row:
            cursor.execute('''
            UPDATE site_translations
            SET text_en = ?, text_zh = ?, category = ?, updated_at = ?
            WHERE key = ?
            ''', (text_en, text_zh, category, now_str, k))
            updated += 1
        else:
            cursor.execute('''
            INSERT INTO site_translations (key, category, text_en, text_zh, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (k, category, text_en, text_zh, now_str))
            inserted += 1

    conn.commit()
    conn.close()
    print(f">> Successfully synced translations in SQLite DB: {inserted} inserted, {updated} updated, {len(all_keys)} total keys.")

if __name__ == '__main__':
    seed_database()
