import sqlite3
import json
import os
from server import DB_PATH, get_default_accounting_detail_en, get_default_accounting_detail_zh

print(f"Connecting to database: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

detail_en = get_default_accounting_detail_en()
detail_zh = get_default_accounting_detail_zh()

modules_en = [f"{m['title']}: {m['desc']}" for m in detail_en['curriculum_modules']]
modules_zh = [f"{m['title']}: {m['desc']}" for m in detail_zh['curriculum_modules']]

cursor.execute("""
UPDATE programs 
SET detail_json_en = ?, 
    detail_json_zh = ?,
    modules_en = ?,
    modules_zh = ?
WHERE slug = 'accounting'
""", (
    json.dumps(detail_en, ensure_ascii=False),
    json.dumps(detail_zh, ensure_ascii=False),
    json.dumps(modules_en, ensure_ascii=False),
    json.dumps(modules_zh, ensure_ascii=False)
))

conn.commit()
print("Accounting record updated successfully in database.")
cursor.execute("SELECT id, slug, title_en, LENGTH(detail_json_en), LENGTH(detail_json_zh) FROM programs WHERE slug = 'accounting'")
row = cursor.fetchone()
print("Updated accounting row:", row)
conn.close()
