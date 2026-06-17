import os, sys, io, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# A4 modeļi un to modifikāciju skaiti
print('=== A4 modeļi un modifikācijas ===')
cur.execute("""
    SELECT cm.id, cm.name, COUNT(cmod.id) as mod_count
    FROM selector_carmodel cm
    LEFT JOIN selector_carmodification cmod ON cmod.car_model_id=cm.id
    WHERE cm.name LIKE 'A4%' AND cm.brand_id=5
    GROUP BY cm.id
    ORDER BY cm.name
""")
for row in cur.fetchall():
    print(f'  id={row[0]}: "{row[1]}" -> {row[2]} modif.')

# Kopā modifikācijas brand_id=5 Audi
print('\n=== Audi (id=5) modifikāciju kopskaits ===')
cur.execute("""
    SELECT COUNT(cmod.id) FROM selector_carmodification cmod
    JOIN selector_carmodel cm ON cmod.car_model_id=cm.id
    WHERE cm.brand_id=5
""")
print(f'Modifikācijas: {cur.fetchone()[0]}')

# Jaunākās modifikācijas (pēdējās 20)
print('\n=== Jaunākās modifikācijas (id pēc kārtas) ===')
cur.execute("""
    SELECT cmod.id, cmod.name, cm.name, cb.name
    FROM selector_carmodification cmod
    JOIN selector_carmodel cm ON cmod.car_model_id=cm.id
    JOIN selector_carbrand cb ON cm.brand_id=cb.id
    ORDER BY cmod.id DESC LIMIT 20
""")
for row in cur.fetchall():
    print(f'  mod_id={row[0]}: "{row[1]}" | modelis="{row[2]}" | marka="{row[3]}"')

# Modeļi bez modifikācijām brand_id=5 (Audi)
print('\n=== Audi (id=5) modeļi bez modif. ===')
cur.execute("""
    SELECT cm.name FROM selector_carmodel cm
    WHERE cm.brand_id=5
    AND NOT EXISTS (SELECT 1 FROM selector_carmodification WHERE car_model_id=cm.id)
    ORDER BY cm.name
""")
rows = cur.fetchall()
print(f'Skaits: {len(rows)}')
for row in rows[:10]:
    print(f'  "{row[0]}"')

conn.close()
