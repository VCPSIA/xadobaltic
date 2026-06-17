import requests, urllib3, sys, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Authorization': 'Basic bGltbzpsaW1v',
    'Referer': 'https://www.liqui-moly.com/',
})

def get(url, **kw):
    r = SESSION.get(url, timeout=20, verify=False, **kw)
    return r

OAPI = 'https://openapi.liqui-moly.com'

# 1. Swagger/docs
print("=== API Docs ===")
docs = ['/swagger', '/swagger.json', '/swagger/ui', '/api', '/api/v2', '/docs', '/openapi.json', '/api-docs']
for ep in docs:
    r = get(f'{OAPI}{ep}')
    if r.status_code != 404:
        print(f"{ep} → {r.status_code}: {r.text[:200].replace(chr(10),' ')}")

# 2. Pilnais kļūdas ziņojums
print("\n=== Pilnā kļūda ===")
r = get(f'{OAPI}/api/v2/oww/brands?client_id=10')
import json
try:
    err = json.loads(r.text)
    print(json.dumps(err, indent=2)[:2000])
except:
    print(r.text[:1000])

# 3. Mēģina ar locale URL ceļā (kā search API: /DEU/DEU/)
print("\n=== OWW ar locale ceļā ===")
locales = [
    f'/api/v2/oww/ENG/ENG/brands?client_id=10',
    f'/api/v2/oww/DEU/DEU/brands?client_id=10',
    f'/api/v2/oww/ENG/brands?client_id=10',
    f'/api/v2/oww/en/brands?client_id=10',
    f'/api/v2/oww/en/en/brands?client_id=10',
    f'/api/v2/oww/brands?client_id=10&locale=en_GB',
    f'/api/v2/oww/brands?client_id=10&lang=ENG',
    f'/api/v2/oww/brands?client_id=10&language=en&country=DE',
    f'/api/v2/oww/brands?client_id=10&store=limo_com_de_de',
]
for ep in locales:
    r = get(f'{OAPI}{ep}')
    ct = r.headers.get('content-type','')
    print(f"{ep}")
    print(f"  → {r.status_code} [{ct[:25]}]: {r.text[:150].replace(chr(10),' ')}")

# 4. Pamēģina DE oil guide ar laukuma meklēšanu
print("\n=== DE oil guide lauka OWW konfigurācija ===")
r = get('https://www.liqui-moly.com/de/service/oelratgeber.html')
html = r.text
# Meklē pilno x-magento-init OWW komponentu
oww_init = re.findall(r'"Oww[^"]*"\s*:\s*\{[^}]{0,500}', html)
for o in oww_init:
    print(f"  {o[:400]}")

# Meklē "owwPlugin" vai "oww_plugin"
plugin = re.findall(r'(?:owwPlugin|oww_plugin|owwUrl|oww-url|owwApiUrl|oww.*?url)[^<]{0,200}', html, re.I)
for p in plugin:
    print(f"  Plugin: {p[:200]}")
