import psycopg2
import json
import csv
from io import StringIO

conn = psycopg2.connect('postgresql://postgres:admin123@localhost:5432/policy_db')
cur = conn.cursor()
cur.execute('SELECT id, tags FROM policies;')
rows = cur.fetchall()
updated = 0
for r in rows:
    if not r[1]: continue
    tags_str = r[1].strip()
    if tags_str.startswith('{') and tags_str.endswith('}'):
        content = tags_str[1:-1]
        if not content:
            tags_list = []
        else:
            reader = csv.reader(StringIO(content), quotechar='"')
            try:
                tags_list = next(reader)
            except StopIteration:
                tags_list = []
        
        new_tags = json.dumps(tags_list)
        cur.execute('UPDATE policies SET tags = %s WHERE id = %s', (new_tags, r[0]))
        updated += 1

conn.commit()
print('Updated', updated, 'rows')
