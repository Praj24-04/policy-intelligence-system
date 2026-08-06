"""
Fix malformed tags in the policies table.
PostgreSQL array format {a,"b c",d} -> JSON ["a","b c","d"]
"""
import psycopg2
import psycopg2.extras
import json
import csv
import io

DB_URL = "postgresql://postgres:admin123@localhost:5432/policy_db"


def pg_array_to_list(raw: str) -> list:
    """Parse a PostgreSQL text array literal like {foo,"bar baz",qux} into a Python list."""
    raw = raw.strip()
    if raw.startswith("{") and raw.endswith("}"):
        raw = raw[1:-1]
    # Use csv reader to handle quoted fields correctly
    reader = csv.reader(io.StringIO(raw), skipinitialspace=True)
    for row in reader:
        return [item.strip() for item in row if item.strip()]
    return []


def main():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, tags FROM policies")
    rows = cur.fetchall()

    fixed = 0
    errors = 0
    for r in rows:
        raw = r["tags"] or "[]"
        try:
            json.loads(raw)
            # Already valid JSON — skip
        except Exception:
            try:
                tags_list = pg_array_to_list(raw)
                new_json = json.dumps(tags_list)
                cur.execute(
                    "UPDATE policies SET tags = %s WHERE id = %s",
                    (new_json, r["id"]),
                )
                fixed += 1
                print(f"  FIXED [{r['id']}] -> {tags_list[:4]}...")
            except Exception as e:
                print(f"  ERROR [{r['id']}]: {e}")
                errors += 1

    conn.commit()
    conn.close()
    print(f"\nDone. Fixed={fixed}, Errors={errors}, Total={len(rows)}")


if __name__ == "__main__":
    main()
