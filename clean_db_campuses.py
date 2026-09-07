import sqlite3
import json
import re

DB_PATH = 'data/victoria.db'

def clean_database():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. settings table
    cur.execute("SELECT key, value FROM settings WHERE key = 'system_prompt'")
    row = cur.fetchone()
    if row:
        sp_val = row['value']
        lines = sp_val.split('\n')
        new_lines = []
        for line in lines:
            if 'North York Campus' in line or '306 Consumers' in line:
                continue
            if 'two convenient Greater Toronto Area campuses' in line:
                line = line.replace('two convenient Greater Toronto Area campuses', 'a modern Greater Toronto Area campus')
            new_lines.append(line)
        new_sp = '\n'.join(new_lines)
        cur.execute("UPDATE settings SET value = ? WHERE key = 'system_prompt'", (new_sp,))
        print("Updated settings.system_prompt")

    # 2. knowledge_base table
    cur.execute("SELECT id, title, content, keywords FROM knowledge_base")
    for r in cur.fetchall():
        cid = r['id']
        content = r['content']
        keywords = r['keywords'] or ''
        changed = False

        if 'North York' in content or '306 Consumers' in content or '北约克' in content or 'two convenient' in content:
            content = content.replace('Victoria International College has two convenient Greater Toronto Area campuses:\n1) Markham Campus (Main): 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8\n2) North York Campus: 306 Consumers Rd., North York, ON M2J 1P8', 
                                      'Victoria International College Markham Main Campus is located at 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8')
            content = content.replace('2) North York Campus: 306 Consumers Rd., North York, ON M2J 1P8\n', '')
            content = content.replace('2) North York Campus: 306 Consumers Rd., North York, ON M2J 1P8', '')
            content = content.replace('📍 North York Campus: 306 Consumers Rd., North York, ON M2J 1P8\n', '')
            content = content.replace('📍 North York Campus: 306 Consumers Rd., North York, ON M2J 1P8', '')
            content = content.replace('📍 北约克校区：306 Consumers Rd., North York, ON M2J 1P8\n', '')
            content = content.replace('📍 北约克校区：306 Consumers Rd., North York, ON M2J 1P8', '')
            content = content.replace('306 Consumers Rd., North York / ', '')
            content = content.replace(' / 306 Consumers Rd., North York', '')
            changed = True

        if 'north york' in keywords.lower():
            kw_list = [k.strip() for k in keywords.split(',') if k.strip().lower() not in ['north york', 'north york campus', '北约克', '北约克校区']]
            keywords = ', '.join(kw_list)
            changed = True

        if changed:
            cur.execute("UPDATE knowledge_base SET content = ?, keywords = ? WHERE id = ?", (content, keywords, cid))
            print(f"Updated knowledge_base #{cid}")

    # 3. job_fairs table
    cur.execute("SELECT id, location_en, location_zh FROM job_fairs")
    for r in cur.fetchall():
        jid = r['id']
        loc_en = r['location_en'] or ''
        loc_zh = r['location_zh'] or ''
        changed = False

        if 'North York' in loc_en or '306 Consumers' in loc_en:
            loc_en = '7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8'
            changed = True
        if 'North York' in loc_zh or '306 Consumers' in loc_zh or '北约克' in loc_zh:
            loc_zh = '7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8'
            changed = True

        if changed:
            cur.execute("UPDATE job_fairs SET location_en = ?, location_zh = ? WHERE id = ?", (loc_en, loc_zh, jid))
            print(f"Updated job_fairs #{jid}")

    # 4. programs table (detail_json_en, detail_json_zh)
    cur.execute("SELECT id, title_en, detail_json_en, detail_json_zh FROM programs")
    for r in cur.fetchall():
        pid = r['id']
        title_en = r['title_en']
        d_en_str = r['detail_json_en']
        d_zh_str = r['detail_json_zh']
        
        if d_en_str:
            try:
                d_en = json.loads(d_en_str)
                if 'snapshot' in d_en and 'locations' in d_en['snapshot']:
                    loc = d_en['snapshot']['locations']
                    if 'North York' in loc:
                        d_en['snapshot']['locations'] = 'Markham Main Campus / Live Online' if 'Live Online' in loc or 'Online' in loc else ('Markham Main Campus / GTA Daycares' if 'Daycares' in loc or 'GTA' in loc else 'Markham Main Campus / Live Online')
                if 'why_choose' in d_en and 'pillars' in d_en['why_choose']:
                    for p in d_en['why_choose']['pillars']:
                        if 'desc' in p and 'Markham & North York' in p['desc']:
                            p['desc'] = p['desc'].replace('Markham & North York', 'Markham Campus')
                        elif 'desc' in p and 'Markham and North York' in p['desc']:
                            p['desc'] = p['desc'].replace('Markham and North York', 'Markham Campus')
                cur.execute("UPDATE programs SET detail_json_en = ? WHERE id = ?", (json.dumps(d_en, ensure_ascii=False), pid))
                print(f"Updated program EN detail for {title_en}")
            except Exception as e:
                print(f"Error parsing detail_json_en for {title_en}: {e}")

        if d_zh_str:
            try:
                d_zh = json.loads(d_zh_str)
                if 'snapshot' in d_zh and 'locations' in d_zh['snapshot']:
                    loc = d_zh['snapshot']['locations']
                    if '北约克' in loc or 'North York' in loc:
                        d_zh['snapshot']['locations'] = '万锦主校区 / 在线名师直播' if '名师' in loc else ('万锦主校区 / GTA 日托中心' if '日托' in loc else '万锦主校区 / 在线直播')
                if 'why_choose' in d_zh and 'pillars' in d_zh['why_choose']:
                    for p in d_zh['why_choose']['pillars']:
                        if 'desc' in p and ('万锦及北约克校区' in p['desc'] or '万锦与北约克校区' in p['desc']):
                            p['desc'] = p['desc'].replace('万锦及北约克校区', '万锦主校区').replace('万锦与北约克校区', '万锦主校区')
                cur.execute("UPDATE programs SET detail_json_zh = ? WHERE id = ?", (json.dumps(d_zh, ensure_ascii=False), pid))
                print(f"Updated program ZH detail for {title_en}")
            except Exception as e:
                print(f"Error parsing detail_json_zh for {title_en}: {e}")

    # 5. articles table
    cur.execute("SELECT id, title, summary, content, geo_target, meta_title, meta_description FROM articles")
    for r in cur.fetchall():
        aid = r['id']
        title = r['title'] or ''
        summary = r['summary'] or ''
        c = r['content'] or ''
        geo = r['geo_target'] or ''
        meta_t = r['meta_title'] or ''
        meta_d = r['meta_description'] or ''
        changed = False

        if 'Toronto & North York' in title:
            title = title.replace('Toronto & North York', 'Toronto & Markham')
            changed = True
        if 'Toronto & North York' in summary:
            summary = summary.replace('Toronto & North York', 'Toronto & Markham')
            changed = True
        if 'Toronto and North York' in summary:
            summary = summary.replace('Toronto and North York', 'Toronto and Markham')
            changed = True
        if 'Toronto & North York' in geo:
            geo = geo.replace('Toronto & North York', 'Toronto & Markham')
            changed = True
        if 'North York Campus' in geo:
            geo = geo.replace('(North York Campus)', '(GTA Region)')
            changed = True
        if 'Toronto & North York' in meta_t:
            meta_t = meta_t.replace('Toronto & North York', 'Toronto & Markham')
            changed = True
        if 'Toronto & North York' in meta_d:
            meta_d = meta_d.replace('Toronto & North York', 'Toronto & Markham')
            changed = True
        if 'Toronto and North York' in meta_d:
            meta_d = meta_d.replace('Toronto and North York', 'Toronto and Markham')
            changed = True

        # Clean content
        old_c = c
        c = c.replace('306 Consumers Rd., North York, ON M2J 1P8 (Victoria Park & Sheppard)', '7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8 (Woodbine & Steeles)')
        c = c.replace('306 Consumers Rd., North York, ON M2J 1P8', '7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8')
        c = c.replace('306 Consumers Rd. North York', '7050 Woodbine Ave. Markham')
        c = c.replace('North York & Markham Campus Locations', 'Markham Campus Location')
        c = c.replace('Markham & North York Campus Locations', 'Markham Campus Location')
        c = c.replace('North York &amp; Markham Campus Locations', 'Markham Campus Location')
        c = c.replace('Markham &amp; North York Campus Locations', 'Markham Campus Location')
        c = c.replace('at our North York and Markham campuses', 'at our Markham campus')
        c = c.replace('at our Markham and North York campuses', 'at our Markham campus')
        c = c.replace('at our Markham & North York campuses', 'at our Markham campus')
        c = c.replace('at our Markham &amp; North York campuses', 'at our Markham campus')
        c = c.replace('at our North York & Markham campuses', 'at our Markham campus')
        c = c.replace('at our North York &amp; Markham campuses', 'at our Markham campus')
        c = c.replace('Our campuses in <strong>Markham</strong> and <strong>North York</strong>', 'Our campus in <strong>Markham</strong>')
        c = c.replace('Our campuses in Markham and North York', 'Our campus in Markham')
        c = c.replace('campus locations in Markham and North York', 'campus in Markham')
        c = c.replace('campuses in Markham and North York', 'campus in Markham')
        c = c.replace('campuses in Markham & North York', 'campus in Markham')
        c = c.replace('campuses in Markham &amp; North York', 'campus in Markham')
        c = c.replace('campuses in the following locations:', 'campus location:')
        c = c.replace('campus locations in the following locations:', 'campus location:')
        c = c.replace('Victoria International College has campuses conveniently located in Markham and North York, making it accessible for residents throughout the Greater Toronto Area (GTA).', 'Victoria International College has its main campus conveniently located in Markham, making it accessible for residents throughout the Greater Toronto Area (GTA).')
        c = c.replace('万锦及北约克两大校区', '万锦主校区')
        c = c.replace('万锦与北约克校区', '万锦主校区')
        c = c.replace('万锦及北约克校区', '万锦主校区')
        
        # Regex patterns for campus lists & blocks
        c = re.sub(r'<p>\s*And our North York campus is located at:.*?</p>\s*<blockquote>.*?</blockquote>', '', c, flags=re.DOTALL | re.IGNORECASE)
        c = re.sub(r'<blockquote>\s*Victoria International College<br>.*?North York.*?</blockquote>', '', c, flags=re.DOTALL | re.IGNORECASE)
        c = re.sub(r'<li>\s*<strong>?📍?\s*Victoria International College\s*-\s*North York Campus:?.*?</li>', '', c, flags=re.IGNORECASE)
        c = re.sub(r'<li>\s*<strong>?📍?\s*North York(?: Campus)?:?.*?</li>', '', c, flags=re.IGNORECASE)
        c = re.sub(r'<li>\s*North York(?: Campus)?:?.*?</li>', '', c, flags=re.IGNORECASE)
        c = re.sub(r'<li>\s*<strong>?📍?\s*北约克(?:校区)?:?.*?</li>', '', c, flags=re.IGNORECASE)
        
        # Replace arbitrary mock Markham addresses with real address
        c = re.sub(r'Markham Campus:\s*(?:1234 Trade St\.|123 Trade Street|1234 Main St\.|456 College Ave|123 Trade Avenue).*?(?=</li>|</p>|</strong>)', 
                   'Markham Main Campus: 7050 Woodbine Ave., Unit 300, Markham, ON L3R 4G8', c)
        c = re.sub(r'<blockquote>\s*Victoria International College<br>123 Trade Street<br>Markham, ON L3R 0A1\s*</blockquote>',
                   '<blockquote>Victoria International College<br>7050 Woodbine Ave., Unit 300<br>Markham, ON L3R 4G8</blockquote>', c)

        if c != old_c:
            changed = True

        if changed:
            cur.execute("""UPDATE articles SET 
                title = ?, summary = ?, content = ?, geo_target = ?, meta_title = ?, meta_description = ? 
                WHERE id = ?""", 
                (title, summary, c, geo, meta_t, meta_d, aid))
            print(f"Updated article #{aid} - {title}")

    conn.commit()
    conn.close()
    print("Database cleanup complete!")

if __name__ == '__main__':
    clean_database()
