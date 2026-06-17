"""Meklē LM produktu specifikācijas (OEM apstiprinājumus)"""
import requests, urllib3, sys, json, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Authorization': 'Basic bGltbzpsaW1v',
    'Accept-Language': 'de-DE,de;q=0.9',
})

def get(url, **kw):
    r = SESSION.get(url, timeout=20, verify=False, **kw)
    if r.status_code == 200:
        try: return r.json()
        except: return r.text
    return None

OAPI = 'https://openapi.liqui-moly.com'

# BMW 116d ieteiktie produkti
PRODUCTS = {
    'P005106': 'Top Tec 4210 0W-30',
    'P000323': 'Top Tec 4200 5W-30 New Generation',
    'P003758': 'Longlife III 5W-30',
}

print("=== LM produktu spec API meklēšana ===")

# Pamēģina produkta API ceļus
for prod_id, prod_name in PRODUCTS.items():
    pid = prod_id.lower()
    print(f"\nProdukts: {prod_name} ({prod_id})")

    tests = [
        f'{OAPI}/api/v2/public/products/{prod_id}/',
        f'{OAPI}/api/v2/public/products/{pid}/',
        f'{OAPI}/api/v2/products/{prod_id}/',
        f'{OAPI}/api/v2/products/{pid}/',
        f'{OAPI}/api/v2/public/product/{prod_id}/',
        f'{OAPI}/api/v1/products/{prod_id}/',
    ]
    for url in tests:
        r = SESSION.get(url, timeout=10, verify=False)
        if r.status_code == 200:
            print(f"  OK: {url}")
            print(f"  {r.text[:300]}")
            break
        elif r.status_code != 404:
            print(f"  {r.status_code}: {url.replace(OAPI,'')}")

# Meklē produktu specifikācijas no LM mājas lapas
print("\n\n=== LM mājas lapas produktu lapa ===")
lm_prod_url = f'https://www.liqui-moly.com/de/de/p/top-tec-4210-0w-30-{PRODUCTS["P005106"].lower().replace(" ","-")}.html'
r_web = SESSION.get(f'https://www.liqui-moly.com/de/de/tinyurl/P005106', timeout=15, verify=False, allow_redirects=True)
print(f"TinyURL status: {r_web.status_code}, final URL: {r_web.url}")

if r_web.status_code == 200:
    html = r_web.text
    # Meklē OEM apstiprinājumus
    oem = re.findall(r'(?:BMW|VW|Mercedes|Volkswagen|Renault|PSA|ACEA|API)[^<"\']{3,60}(?:Longlife|LL|504|507|229|208|C2|C3|SN|SM)[^<"\']{0,30}', html)
    print(f"OEM atrašanās: {oem[:10]}")

    # Meklē JSON-LD datus
    json_ld = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S)
    for jl in json_ld[:2]:
        print(f"\nJSON-LD: {jl[:500]}")

    # Meklē specifikāciju tabulu
    specs = re.findall(r'(?:Freigaben|approvals|specifications)[^<]{0,200}', html, re.I)
    for s in specs[:3]:
        print(f"Spec: {s[:200]}")

# Meklē atsevišķu specifikāciju API
print("\n\n=== Specifikāciju API ===")
spec_tests = [
    f'{OAPI}/api/v2/public/specifications/',
    f'{OAPI}/api/v2/public/specs/',
    f'{OAPI}/api/v2/public/approvals/',
    f'{OAPI}/api/v2/public/product-specs/',
    f'{OAPI}/api/v2/oww/10/DEU/DEU/product/P005106/',
]
for url in spec_tests:
    r = SESSION.get(url, timeout=10, verify=False)
    if r.status_code != 404:
        print(f"  {r.status_code}: {url.replace(OAPI,'')}: {r.text[:150]}")
