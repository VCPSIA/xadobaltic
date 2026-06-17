import requests, urllib3, sys, re, json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

# Sesija bez auth headera
SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
})

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

# 1. Vispirms iegūst sesijas cookies
print("=== Iegūst sesiju ===")
r0 = get('https://www.liqui-moly.com/de/de/')
print(f"Mājas lapa: {r0.status_code}")
print(f"Cookies: {dict(r0.cookies)}")
print(f"Headers: {dict(list(r0.headers.items())[:5])}")

# 2. Iegūst oil guide lapu ar sesiju
r1 = get('https://www.liqui-moly.com/de/service/oelratgeber.html')
print(f"Oil guide: {r1.status_code}, cookies: {list(SESSION.cookies.keys())}")

# 3. Mēģina API ar sesijas cookies
OAPI = 'https://openapi.liqui-moly.com'
print("\n=== API bez Authorization ===")
SESSION.headers.update({
    'Accept': 'application/json, */*',
    'Origin': 'https://www.liqui-moly.com',
    'X-Requested-With': 'XMLHttpRequest',
})

r2 = get(f'{OAPI}/api/v2/oww/brands?client_id=10')
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text[:500]}")

# 4. Mēģina ar Authorization
SESSION.headers.update({'Authorization': 'Basic bGltbzpsaW1v'})
r3 = get(f'{OAPI}/api/v2/oww/brands?client_id=10')
print(f"\nAr Auth: {r3.status_code}: {r3.text[:300]}")

# 5. Meklē OWW JS bundle no lapas
print("\n=== requirejs-map analīze - pilna ===")
rmap = get('https://liquimoly.cloudimg.io/v7/https://www.liqui-moly.com/static/version1781527877/frontend/limo/base/en_GB/requirejs-map.min.js?func=proxy&process=minify-js?func=proxy')
map_text = rmap.text

# Meklē Oww moduļus
oww_modules = re.findall(r'"Oww_[^"]+":"[^"]+"', map_text)
for m in oww_modules[:20]:
    print(f"  {m}")

# Meklē limo/search moduļus
limo_modules = re.findall(r'"Limo_[^"]*[Oo]ww[^"]*":"[^"]+"', map_text, re.I)
for m in limo_modules[:10]:
    print(f"  {m}")
