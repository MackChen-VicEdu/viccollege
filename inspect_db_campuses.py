import sqlite3

conn = sqlite3.connect('data/victoria.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r['name'] for r in cur.fetchall()]

for tbl in tables:
    cur.execute(f"PRAGMA table_info({tbl})")
    cols = [c['name'] for c in cur.fetchall()]
    for col in cols:
        try:
            cur.execute(f"SELECT COUNT(*) as cnt FROM {tbl} WHERE {col} LIKE '%North York%' OR {col} LIKE '%Consumers%' OR {col} LIKE '%北约克%'")
            cnt = cur.fetchone()['cnt']
            if cnt > 0:
                print(f"Table {tbl}.{col}: {cnt} rows")
        except Exception:
            pass
