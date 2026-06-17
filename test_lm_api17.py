import requests, urllib3, sys, json, re
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
        return None

BASE = '/api/v2/oww/10/DEU/DEU'

# BMW 116d pilnā atbilde
rec = get(f'{BASE}/1/1357ff763462e849/6395932947595f89/bd699ba8a513d04b/')
print("=== BMW 116d PILNĀ JSON ATBILDE ===")
print(json.dumps(rec, indent=2, ensure_ascii=False)[:5000])

# Ekstrahē viskozitātes no produktu nosaukumiem
print("\n=== VISKOZITĀTES EKSTRAKCIJA ===")
viscs = set()
motor_results = rec.get('results', {}).get('Motor', {})
for use_name, use_data in motor_results.get('uses', {}).items():
    for prod_id, prod in use_data.get('products', {}).items():
        name = prod.get('name', '')
        matches = re.findall(r'\b\d+W[-–]\d+\b', name, re.I)
        if matches:
            viscs.update(matches)
            print(f"  {name} → {matches}")

print(f"\nKopā viskozitātes: {viscs}")

# Skatāmies arī "specifications" vai citus laukus
print("\n=== VISAS ATBILDES ATSLĒGAS ===")
def print_keys(d, prefix=''):
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                print(f"{prefix}{k}: [{type(v).__name__}]")
                print_keys(v, prefix + '  ')
            else:
                print(f"{prefix}{k}: {str(v)[:80]}")
    elif isinstance(d, list) and d:
        print(f"{prefix}[0]:")
        print_keys(d[0], prefix + '  ')

print_keys(rec)
