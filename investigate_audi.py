import os, sys, io, sqlite3
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Tieši SQL vaicājums uz SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Audi markas
print('=== Audi markas (tieši no SQLite) ===')
cur.execute("SELECT id, name FROM selector_carbrand WHERE name LIKE '%udi%'")
for row in cur.fetchall():
    print(f'  id={row[0]}: "{row[1]}"')
    cur2 = conn.cursor()
    cur2.execute("SELECT COUNT(*) FROM selector_carmodel WHERE brand_id=?", (row[0],))
    mc = cur2.fetchone()[0]
    print(f'    -> {mc} modeļi')

# Modeļi brand_id=30
print('\n=== Modeļi brand_id=30 ===')
cur.execute("SELECT COUNT(*) FROM selector_carmodel WHERE brand_id=30")
print(f'Skaits: {cur.fetchone()[0]}')

cur.execute("SELECT id, name, brand_id FROM selector_carmodel WHERE brand_id=30 LIMIT 5")
for row in cur.fetchall():
    print(f'  id={row[0]}: "{row[1]}" brand_id={row[2]}')

# Visi modeļi ar A4
print('\n=== Modeļi ar "A4" ===')
cur.execute("SELECT cm.id, cm.name, cm.brand_id, cb.name FROM selector_carmodel cm JOIN selector_carbrand cb ON cm.brand_id=cb.id WHERE cm.name LIKE 'A4%' LIMIT 10")
for row in cur.fetchall():
    print(f'  model_id={row[0]}: "{row[1]}" -> brand_id={row[2]} "{row[3]}"')

# Modifikācijas skaits brand_id=30 modeļiem
print('\n=== Modifikācijas modeļiem ar brand_id IN (30,31) ===')
cur.execute("""
    SELECT cb.name, cm.name, COUNT(cmod.id)
    FROM selector_carbrand cb
    JOIN selector_carmodel cm ON cm.brand_id=cb.id
    LEFT JOIN selector_carmodification cmod ON cmod.car_model_id=cm.id
    WHERE cb.id IN (30, 31)
    GROUP BY cm.id
    ORDER BY cb.name, cm.name
    LIMIT 20
""")
for row in cur.fetchall():
    print(f'  {row[0]} / {row[1]}: {row[2]} modif.')

conn.close()
