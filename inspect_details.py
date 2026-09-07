import sqlite3
import json

conn = sqlite3.connect('data/victoria.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- SETTINGS ---")
cur.execute("SELECT key, value FROM settings WHERE value LIKE '%North York%' OR value LIKE '%北约克%'")
for r in cur.fetchall():
    print(r['key'], "->", r['value'])

print("\n--- KNOWLEDGE BASE ---")
cur.execute("SELECT id, title, content FROM knowledge_base WHERE content LIKE '%North York%' OR content LIKE '%北约克%' OR keywords LIKE '%north york%'")
for r in cur.fetchall():
    print(r['id'], r['title'], "->", r['content'])

print("\n--- JOB FAIRS ---")
cur.execute("SELECT id, title_en, location_en, location_zh FROM job_fairs WHERE location_en LIKE '%North York%' OR location_zh LIKE '%North York%' OR location_zh LIKE '%北约克%'")
for r in cur.fetchall():
    print(r['id'], r['title_en'], "EN:", r['location_en'], "ZH:", r['location_zh'])

print("\n--- SITE TRANSLATIONS ---")
cur.execute("SELECT key, text_en, text_zh FROM site_translations WHERE text_en LIKE '%North York%' OR text_zh LIKE '%North York%' OR text_zh LIKE '%北约克%'")
for r in cur.fetchall():
    print(r['key'], "EN:", r['text_en'], "ZH:", r['text_zh'])

print("\n--- PROGRAMS DETAIL JSON ---")
cur.execute("SELECT code, detail_json_en, detail_json_zh FROM programs")
for r in cur.fetchall():
    for lang, json_str in [('en', r['detail_json_en']), ('zh', r['detail_json_zh'])]:
        if json_str and ('North York' in json_str or '北约克' in json_str or 'Consumers' in json_str):
            print(r['code'], lang, "has match")
