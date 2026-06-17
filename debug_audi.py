import os, sys, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

import xado_ua_import as imp

# Audi (EU) = ua_brand_id=26, vt_id=1
# Testa modelis: A3, S3, 8L = ua_model_id=2397

print("=== Testē getTypes tieši ===")
tests = [
    ('2397', 'A3, S3, 8L'),
    ('2403', 'A4, S4, RS 4, 8D'),
    ('2422', 'A8, S8, 4D'),
]

for ua_mid, name in tests:
    tresp = imp.post_api('getTypes', {
        'vehicle_type_id': 1,
        'vehicle_type_make_id': '26',
        'vehicle_type_make_model_id': ua_mid,
    })
    if not tresp:
        print(f"  {name}: NULL atbilde")
        continue
    mods = [(v,t) for v,t in imp.parse_options(tresp.get('html','')) if v != '0']
    print(f"  {name}: {len(mods)} modifikacijas")
    for v,t in mods[:3]:
        print(f"    uid={v}: {t}")
    time.sleep(0.5)

# Pārbauda vai fill_mods log apstrādāja Audi
print()
print("=== fill_mods log Audi rindiņas ===")
try:
    with open('fill_mods_log.txt', encoding='utf-8') as f:
        lines = f.readlines()
    audi_lines = [l.rstrip() for l in lines if 'audi' in l.lower() or 'Audi' in l]
    for l in audi_lines:
        print(l)
except Exception as e:
    print(f"Log kļūda: {e}")
