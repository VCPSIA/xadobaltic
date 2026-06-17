import requests, urllib3, sys, re, base64
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

# Dekodē authToken
token = base64.b64decode('bGltbzpsaW1v').decode()
print(f"authToken: {token}")  # → limo:limo

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.liqui-moly.com/de/service/oelratgeber.html',
    'Authorization': f'Basic bGltbzpsaW1v',
})

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

OAPI = 'https://openapi.liqui-moly.com'
CLIENT_ID = '10'

# === OWW API ar autorizāciju ===
print("\n=== OWW API ar Basic Auth (limo:limo) ===")
tests = [
    f'/api/v2/oww/brands?client_id={CLIENT_ID}',
    f'/api/v2/oww/manufacturers?client_id={CLIENT_ID}',
    f'/api/v2/oww/cars?client_id={CLIENT_ID}',
    f'/api/v2/oww/vehicles?client_id={CLIENT_ID}',
    f'/api/v2/oww/brand/list?client_id={CLIENT_ID}',
    f'/api/v1/oww/brands?client_id={CLIENT_ID}',
    f'/api/v2/oww/?client_id={CLIENT_ID}',
]

for ep in tests:
    r = get(f'{OAPI}{ep}')
    ct = r.headers.get('content-type', '')
    preview = r.text[:300].replace('\n', ' ')
    print(f"\n{ep}")
    print(f"  {r.status_code} [{ct[:30]}]")
    print(f"  {preview[:250]}")

# === Pamēģina arī search API ===
print("\n\n=== Search API ===")
search_url = 'https://openapi.liqui-moly.com/api/v2/search/limo_com_de_de/magento2_product_7/DEU/DEU/'
r = get(search_url + '?q=motoröl')
print(f"Search status: {r.status_code}")
print(f"Preview: {r.text[:400]}")
