import sqlite3, os
db = r'D:\openclaw\.openclaw\Morpheus\data\projects\b8fa8f17-b057-48b1-accb-99c255c31115\novelist.db'
conn = sqlite3.connect(db)

for table, cols in [
    ('character_templates', [('role_type', "TEXT DEFAULT 'other'"), ('motivation', "TEXT DEFAULT ''")]),
    ('character_states', [('status', "TEXT DEFAULT ''"), ('weapons', "TEXT DEFAULT '[]'"), ('battle_power', "TEXT DEFAULT ''")]),
]:
    existing = {r[1] for r in conn.execute(f'PRAGMA table_info({table})').fetchall()}
    for col, defn in cols:
        if col not in existing:
            conn.execute(f'ALTER TABLE {table} ADD COLUMN {col} {defn}')
            print(f'Added {col} to {table}')

conn.commit()
conn.close()
print('Done')
