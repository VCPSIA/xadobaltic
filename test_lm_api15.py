import requests, urllib3, sys, re, json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Authorization': 'Basic bGltbzpsaW1v',
    'Referer': 'https://www.liqui-moly.com/de/service/oelratgeber.html',
    'Origin': 'https://www.liqui-moly.com',
})

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

OAPI = 'https://openapi.liqui-moly.com'
C = '10'  # clientId

# Hash formāts: #oww:/api/v2/oww/{clientId}/{countryCode}/{languageCode}/{defaultCategory}/
# Tātad API URL: /api/v2/oww/{clientId}/{countryCode}/{languageCode}/{category}/{endpoint}

print("=== OWW API ar {clientId}/{country}/{lang}/{cat}/{endpoint} formātu ===")
tests = [
    f'/api/v2/oww/{C}/DEU/DEU/1/brands',
    f'/api/v2/oww/{C}/DEU/DEU/1/manufacturers',
    f'/api/v2/oww/{C}/DEU/DEU/brands',
    f'/api/v2/oww/{C}/DEU/DEU/',
    f'/api/v2/oww/{C}/DEU/ENG/1/brands',
    f'/api/v2/oww/{C}/ENG/ENG/1/brands',
    f'/api/v2/oww/{C}/DEU/DEU/1/',
    f'/api/v2/oww/DEU/DEU/{C}/1/brands',
    f'/api/v2/oww/DEU/DEU/1/{C}/brands',
]
for ep in tests:
    r = get(f'{OAPI}{ep}')
    ct = r.headers.get('content-type','')
    preview = r.text[:300].replace('\n',' ')
    print(f"\n{ep}")
    print(f"  {r.status_code} [{ct[:30]}]: {preview[:200]}")

# Skatāmies /oww2 lapu
print("\n\n=== /oww2 lapa ===")
r_oww2 = get('https://www.liqui-moly.com/oww2')
print(f"  /oww2 → {r_oww2.status_code}")
r_oww2_de = get('https://www.liqui-moly.com/de/de/oww2')
print(f"  /de/de/oww2 → {r_oww2_de.status_code}: {r_oww2_de.text[:200]}")

# Parametri
params_oww2 = f'https://www.liqui-moly.com/de/de/oww2?vehicle_types=1,32,2,3,4,5,10,31&tabs=vehicleSelect&clientId={C}'
r_oww2p = get(params_oww2)
print(f"  /de/de/oww2?params → {r_oww2p.status_code}: {r_oww2p.text[:300]}")

# Skatāmies oww-vehicle-service.min.js pilnāku kodu
print("\n\n=== oww-vehicle-service.min.js pilns kods ===")
V = 'version1781527877'
CDN_BASE = f'https://liquimoly.cloudimg.io/v7/https://www.liqui-moly.com/static/{V}/frontend/Magento/base/default'
r_js = get(f'{CDN_BASE}/Limo_Search/js/components/oww-vehicle-service.min.js?func=proxy&process=minify-js')
print(r_js.text)
