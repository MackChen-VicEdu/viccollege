import sqlite3
from datetime import datetime

DB_PATH = 'data/victoria.db'

def fix_psw_durations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    now_str = datetime.utcnow().isoformat()

    print(">>> 1. Updating Settings (system_prompt)...")
    cursor.execute("SELECT value FROM settings WHERE key = 'system_prompt'")
    sp_row = cursor.fetchone()
    if sp_row and sp_row['value']:
        old_val = sp_row['value']
        new_val = old_val.replace('PSW DE 2022): 30 weeks', 'PSW DE 2022): 23 weeks')
        new_val = new_val.replace('PSW DE 2022): 30 周', 'PSW DE 2022): 23 周')
        if old_val != new_val:
            cursor.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = 'system_prompt'", (new_val, now_str))
            print("  -> Updated system_prompt to 23 weeks successfully!")
        else:
            print("  -> system_prompt was already up to date or had no match.")

    print("\n>>> 2. Updating Knowledge Base (PSW items)...")
    psw_kb_content = (
        "The NACC Personal Support Worker (PSW) DE 2022 Certificate Program is an intensive 23-week accredited program "
        "consisting of classroom/online theory, hands-on clinical lab simulations at our campuses, and 300+ hours of guaranteed "
        "clinical practicum placement in leading Ontario nursing homes and healthcare facilities. "
        "Graduates receive their official NACC PSW Certificate, Standard First Aid & CPR Level C certification. "
        "High employment demand across hospitals, long-term care homes, and community healthcare with $20-$28/hr starting wage. "
        "Better Jobs Ontario government funding grants (up to $28,000+) are applicable."
    )
    cursor.execute("""
    UPDATE knowledge_base
    SET keywords = 'psw, personal support worker, healthcare, nursing home, clinic, practicum placement, cpr, first aid, nacc, caregiving, hospital, medical, duration, how long, 23 weeks, 23周',
        content = ?,
        updated_at = ?
    WHERE id = 2 OR title LIKE '%Personal Support Worker%'
    """, (psw_kb_content, now_str))
    print(f"  -> Updated {cursor.rowcount} KB items with 23 weeks.")

    print("\n>>> 3. Updating Articles...")
    cursor.execute("SELECT id, content FROM articles")
    articles = cursor.fetchall()
    art_updated = 0
    for art in articles:
        c = art['content'] or ''
        orig_c = c
        c = c.replace('during your 30 weeks of training', 'during your 23 weeks of training')
        c = c.replace('comprehensive 30-week program', 'comprehensive 23-week program')
        c = c.replace('30-week program includes standard classroom theory', '23-week program includes standard classroom theory')
        c = c.replace('PSW DE 2022) 医疗护工文凭</strong>（30周', 'PSW DE 2022) 医疗护工文凭</strong>（23周')
        c = c.replace('PSW DE 2022):</strong> 30 weeks', 'PSW DE 2022):</strong> 23 weeks')
        if c != orig_c:
            cursor.execute("UPDATE articles SET content = ?, updated_at = ? WHERE id = ?", (c, now_str, art['id']))
            art_updated += 1
            print(f"  -> Updated Article ID {art['id']}")

    print(f"  -> Total {art_updated} articles updated.")

    conn.commit()
    conn.close()
    print("\n>>> All Database PSW Durations Fixed to 23 Weeks Successfully! <<<")

if __name__ == '__main__':
    fix_psw_durations()
