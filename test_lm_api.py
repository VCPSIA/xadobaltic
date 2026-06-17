import requests, json, urllib3, sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
})

BASE = 'https://www.liqui-moly.com'

def get(url, **kw):
    return SESSION.get(url, timeout=15, verify=False, **kw)

# 1. Meklē JS bundle failus kurā var būt API URL
print("=== Meklē API endpointus lapā ===")
r = get(f'{BASE}/en/service/oil-guide.html')
print(f"Status: {r.status_code}")

# Meklē src= JS failus
import re
js_files = re.findall(r'src="([^"]*\.js[^"]*)"', r.text)
print(f"JS faili: {js_files[:5]}")

# Meklē API saites
api_hints = re.findall(r'["\']([^"\']*(?:api|oilguide|oil-guide|vehicle|brand|manufacturer)[^"\']*)["\']', r.text, re.I)
for h in set(api_hints[:20]):
    print(f"  HINT: {h}")

# 2. Endpoint testi
print("\n=== Endpoint testi ===")
test_endpoints = [
    '/en/service/oil-guide/brands.json',
    '/en/service/oil-guide/api/brands',
    '/api/oil-guide/car-brands',
    '/en/api/oilguide/manufacturers',
    '/service/oil-guide/car-manufacturers',
]
for ep in test_endpoints:
    try:
        r = get(f'{BASE}{ep}')
        print(f"{ep} → {r.status_code} | {r.text[:80].replace(chr(10),' ')}")
    except Exception as e:
        print(f"{ep} → ERR: {e}")
