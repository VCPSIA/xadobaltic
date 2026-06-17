import requests, urllib3, sys, json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Authorization': 'Basic bGltbzpsaW1v',
    'Referer': 'https://www.liqui-moly.com/de/service/oelratgeber.html',
})

def get(url):
    r = SESSION.get(f'https://openapi.liqui-moly.com{url}', timeout=20, verify=False)
    try:
        return r.json()
    except:
        print(f"  RAW: {r.text[:300]}")
        return None

BASE = '/api/v2/oww/10/DEU/DEU'

# 1. Kategorijas
print("=== KATEGORIJAS ===")
cats = get(f'{BASE}/')
print(json.dumps(cats, indent=2, ensure_ascii=False))

# 2. Pkw markas (kategorija 1)
print("\n=== PKW MARKAS (kategorija 1) ===")
brands = get(f'{BASE}/1/')
makes = brands.get('makes', [])
print(f"Skaits: {len(makes)}")
print(json.dumps(makes[:5], indent=2, ensure_ascii=False))

# 3. Abarth modeļi (id: 10be247fe539bb03)
print("\n=== ABARTH MODEĻI ===")
abarth_id = makes[0]['id']
models = get(f'{BASE}/1/{abarth_id}/')
model_list = models.get('models', [])
print(f"Skaits: {len(model_list)}")
print(json.dumps(model_list[:5], indent=2, ensure_ascii=False))

# 4. BMW pirmā modeļa tipi
print("\n=== BMW MARKAS UN MODEĻI ===")
# Atrast BMW
bmw = next((m for m in makes if 'BMW' in m['name'].upper()), None)
if bmw:
    print(f"BMW: {bmw}")
    bmw_models = get(f'{BASE}/1/{bmw["id"]}/')
    bmw_model_list = bmw_models.get('models', [])
    print(f"BMW modeļi: {len(bmw_model_list)}")
    print(json.dumps(bmw_model_list[:3], indent=2, ensure_ascii=False))

    if bmw_model_list:
        first_model = bmw_model_list[0]
        print(f"\nBMW pirmais modelis: {first_model['name']}")
        types = get(f'{BASE}/1/{bmw["id"]}/{first_model["id"]}/')
        type_list = types.get('types', [])
        print(f"Tipi: {len(type_list)}")
        print(json.dumps(type_list[:3], indent=2, ensure_ascii=False))

        # 5. Pirmā tipa rekomendācija
        if type_list:
            first_type = type_list[0]
            print(f"\nPirmā BMW modifikācija: {first_type}")
            # Rekomendācija - šis ir link ko arī OWW widget izmanto
            rec_link = first_type.get('link', '')
            print(f"Recommendation link: {rec_link}")
            rec = get(rec_link)
            print(f"\nRekomendācija JSON:")
            print(json.dumps(rec, indent=2, ensure_ascii=False)[:2000])
