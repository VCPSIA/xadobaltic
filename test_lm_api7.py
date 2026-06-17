import requests, urllib3, sys, re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,*/*',
    'Accept-Language': 'en-US,en;q=0.9',
})

def get(url, **kw):
    return SESSION.get(url, timeout=20, verify=False, **kw)

# Ielādē DE oil guide lapu - tajā bija data-oww-client-id
print("=== DE oil guide HTML analīze ===")
r = get('https://www.liqui-moly.com/de/service/oelratgeber.html')
html = r.text

# Saglabā daļu no HTML
# Meklē oww widget div
oww_divs = re.findall(r'<[^>]*oww[^>]*>([^<]{0,300})', html, re.I)
print(f"OWW div saturs ({len(oww_divs)}):")
for d in oww_divs[:5]:
    print(f"  {d[:200]}")

# Meklē data-oww-* atribūtus ar kontekstu
oww_attrs = re.findall(r'<[^>]*data-oww[^>]{0,500}>', html, re.I)
print(f"\ndata-oww elementi ({len(oww_attrs)}):")
for a in oww_attrs[:5]:
    print(f"  {a[:400]}")

# Meklē x-magento-init (Magento widget config)
magento_inits = re.findall(r'x-magento-init[^>]{0,50}>(.*?)</script>', html, re.S)
print(f"\nx-magento-init ({len(magento_inits)}):")
for m in magento_inits[:3]:
    print(f"  {m[:500]}")

# Meklē Alpine.js x-data
alpine_data = re.findall(r'x-data=["\']([^"\']{0,500})["\']', html)
print(f"\nx-data Alpine.js ({len(alpine_data)}):")
for d in alpine_data[:3]:
    print(f"  {d[:400]}")

# Meklē JSON blokus ar oww
import json
script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html, re.S)
print(f"\nScript tagi: {len(script_tags)}")
for sc in script_tags:
    if 'oww' in sc.lower() or 'oil' in sc.lower() or 'vehicle' in sc.lower():
        print(f"\n  OWW script ({len(sc)} rakstzīmes):")
        print(f"  {sc[:600]}")

# Meklē visas URL kas satur 'oww' vai 'vehicle' vai 'api'
all_urls = re.findall(r'https?://[^\s"\'<>]+', html)
api_urls = [u for u in all_urls if any(x in u.lower() for x in ['oww', 'vehicle', 'brand', 'openapi', '/api/'])]
print(f"\nAPI URLs lapā:")
for u in set(api_urls[:15]):
    print(f"  {u}")
