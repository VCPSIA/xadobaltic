"""Pārbauda OEM specifikācijas LM OWW API atbildē"""
import requests, urllib3, sys, json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json',
    'Authorization': 'Basic bGltbzpsaW1v',
})

def api(path):
    r = SESSION.get(f'https://openapi.liqui-moly.com{path}', timeout=20, verify=False)
    return r.json() if r.status_code == 200 else None

BASE = '/api/v2/oww/10/DEU/DEU'

def show_motor_specs(brand_name, brand_lm_id, model_lm_id, type_lm_id, model_name, type_name):
    rec = api(f'{BASE}/1/{brand_lm_id}/{model_lm_id}/{type_lm_id}/')
    if not rec:
        print("  NAV ATBILDES")
        return
    print(f"\n--- {brand_name}: {model_name} / {type_name} ---")
    motor = rec.get('results', {}).get('Motor', {})
    uses = motor.get('uses', {})
    print(f"  'uses' atslēgas: {list(uses.keys())}")
    for use_name, use_data in uses.items():
        products = [p['name'] for p in use_data.get('products', {}).values()]
        interval = use_data.get('interval', [])
        print(f"  use='{use_name}': interval={interval[:1]}, produkti={products[:3]}")

# BMW
print("=== BMW ===")
bmw_id = '1357ff763462e849'  # BMW EU
bmw_e87_id = '6395932947595f89'  # 1er-Serie E87
bmw_116d_id = 'bd699ba8a513d04b'  # 116d
show_motor_specs('BMW', bmw_id, bmw_e87_id, bmw_116d_id, '1er-Serie E87', '116d')

# VW - meklēsim
print("\n=== VW ===")
vw_brands = api(f'{BASE}/1/')
vw = next((m for m in vw_brands.get('makes', []) if 'Volkswagen (VW) (EU)' in m['name']), None)
if vw:
    print(f"VW id: {vw['id']}")
    vw_models = api(f'{BASE}/1/{vw["id"]}/')
    golf = next((m for m in vw_models.get('models', []) if 'Golf' in m['name'] and 'VII' in m['name']), None)
    if golf:
        print(f"Golf VII id: {golf['id']}")
        golf_types = api(f'{BASE}/1/{vw["id"]}/{golf["id"]}/')
        type1 = golf_types.get('types', [])[0] if golf_types else None
        if type1:
            show_motor_specs('VW', vw['id'], golf['id'], type1['id'], golf['name'], type1['name'])

# Audi - ar DSG un sportu parasti ir specifiski apstiprinājumi
print("\n=== Audi ===")
audi = next((m for m in vw_brands.get('makes', []) if m['name'] == 'Audi (EU)'), None)
if audi:
    audi_models = api(f'{BASE}/1/{audi["id"]}/')
    a4 = next((m for m in audi_models.get('models', []) if 'A4' in m['name'] and 'B8' in m['name']), None)
    if a4:
        a4_types = api(f'{BASE}/1/{audi["id"]}/{a4["id"]}/')
        type1 = a4_types.get('types', [])[0] if a4_types else None
        if type1:
            show_motor_specs('Audi', audi['id'], a4['id'], type1['id'], a4['name'], type1['name'])

# Mercedes
print("\n=== Mercedes ===")
merc = next((m for m in vw_brands.get('makes', []) if 'Mercedes-Benz (EU)' in m['name']), None)
if merc:
    merc_models = api(f'{BASE}/1/{merc["id"]}/')
    cls = merc_models.get('models', [])
    if cls:
        model = cls[0]
        types = api(f'{BASE}/1/{merc["id"]}/{model["id"]}/')
        type1 = types.get('types', [])[0] if types else None
        if type1:
            show_motor_specs('Mercedes', merc['id'], model['id'], type1['id'], model['name'], type1['name'])
