import sqlite3

conn = sqlite3.connect('services/rozgarlink.db')
cur = conn.cursor()

tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("=== TABLES ===")
print(tables)
print()

for t in ['opportunities', 'users', 'student_profiles', 'applications']:
    if t in tables:
        count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"{t}: {count} rows")
        if count > 0 and t == 'opportunities':
            rows = cur.execute(f"SELECT id, category, is_active, title FROM {t} LIMIT 5").fetchall()
            for r in rows:
                print(f"  -> {r}")
    else:
        print(f"{t}: TABLE MISSING")

conn.close()
