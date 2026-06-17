"""Meklē LM produktu specifikāciju iegūšanas ceļu"""
import requests, urllib3, sys, json, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Authorization': 'Basic bGltbzpsaW1v',
})

def get(url):
    r = SESSION.get(url, timeout=15, verify=False)
    if r.status_code == 200:
        try: return r.json()
        except: return r.text[:500]
    return f"HTTP {r.status_code}"

OAPI = 'https://openapi.liqui-moly.com'
LM = 'https://www.liqui-moly.com'

# 1. Izmēģina dažādus produkta API URL formātus
print("=== Produkta API ===")
for path in [
    '/api/v2/oww/10/DEU/DEU/product/P005106',
    '/api/v2/oww/10/DEU/DEU/product/p005106/',
    '/api/v2/public/product/P005106/',
    '/api/v2/public/product/p005106/',
    '/api/v2/public/products/P005106/specs/',
    '/api/v2/oww/product/P005106/',
    '/api/v2/oww/10/product/P005106/',
]:
    r = get(f'{OAPI}{path}')
    print(f"{path}: {str(r)[:200]}")

# 2. Magento REST API produkta spec
print("\n=== Magento REST API ===")
mag_auth = 'Basic bGltbzpsaW1v'
for path in [
    '/rest/default/V1/products/P005106',
    '/rest/de/V1/products/P005106',
    '/rest/V1/products/P005106',
    '/rest/default/V1/products/by-sku/P005106',
]:
    r = SESSION.get(f'{LM}{path}', headers={'Authorization': mag_auth}, timeout=10, verify=False)
    if r.status_code != 404:
        print(f"{path}: {r.status_code}: {r.text[:300]}")

# 3. Iegūst specifikācijas no LM produktu lapas – ātrāka metode
print("\n=== HTML scrape - produktu specifikācijas ===")
products = {
    'P005106': ('Top Tec 4210 0W-30', 'top-tec-4210-0w-30'),
    'P000323': ('Top Tec 4200 5W-30 New Generation', 'top-tec-4200-5w-30-new-generation'),
    'P003758': ('Longlife III 5W-30', 'longtime-high-tech-5w-30'),  # guess
    'P000327': ('Top Tec 4600 5W-30', 'top-tec-4600-5w-30'),
}

def get_product_specs(prod_id):
    """Ielādē LM produkta lapu un izvelk OEM specifikācijas."""
    # Izmanto tinyurl redirect
    r = SESSION.get(f'{LM}/de/de/tinyurl/{prod_id}', timeout=15, verify=False, allow_redirects=True)
    if r.status_code != 200:
        return []
    html = r.text
    # Meklē specifikācijas tabulu / JSON datus
    # Metode 1: JSON bloks ar "approvals" vai "specifications"
    json_blocks = re.findall(r'"(?:approvals|specifications|freigaben)":\s*"([^"]{10,200})"', html, re.I)
    if json_blocks:
        return json_blocks

    # Metode 2: teksts lapā (kā atradu iepriekš)
    specs_raw = re.findall(r'(?:ACEA|API|BMW|VW|Mercedes|Porsche|Renault|PSA)[^"<\n]{3,120}', html)
    # Filtrē tikai īstas specifikāciju rindas (satur LL, SAE, SN, C3 utt.)
    specs = []
    for s in specs_raw:
        if re.search(r'(?:Longlife|LL-\d+|C[23]|SN|SM|504|507|508|229\.\d+|Porsche C)', s):
            specs.append(s.strip()[:150])
    return list(set(specs))[:3]

for prod_id, (prod_name, _) in products.items():
    specs = get_product_specs(prod_id)
    print(f"\n{prod_name} ({prod_id}):")
    for s in specs:
        print(f"  {s}")

# 4. JSON-LD produkta dati
print("\n\n=== JSON-LD produkta dati ===")
r = SESSION.get(f'{LM}/de/de/tinyurl/P005106', timeout=15, verify=False, allow_redirects=True)
html = r.text
json_lds = re.findall(r'type="application/ld\+json">(.*?)</script>', html, re.S)
for jl in json_lds:
    if 'Product' in jl or 'offers' in jl.lower():
        try:
            d = json.loads(jl)
            print(json.dumps(d, indent=2, ensure_ascii=False)[:800])
        except:
            pass
