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

# Ielādē DE oil guide
r = get('https://www.liqui-moly.com/de/service/oelratgeber.html')
html = r.text

# Saglabā HTML failu analīzei
with open('lm_oilguide.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML saglabāts: {len(html)} baiti")

# Meklē <div> ar oww
oww_section = re.findall(r'<div[^>]*oww[^>]*>[\s\S]{0,1000}', html, re.I)
print(f"\nOWW div sekcijas ({len(oww_section)}):")
for s in oww_section[:3]:
    print(f"\n  {s[:600]}")

# Meklē VISU x-magento-init script saturu
print("\n=== Visi x-magento-init ===")
mag_scripts = re.findall(r'<script\s+type=["\']text/x-magento-init["\'][^>]*>([\s\S]*?)</script>', html)
print(f"Skaits: {len(mag_scripts)}")
for sc in mag_scripts:
    if any(x in sc.lower() for x in ['oww', 'vehicle', 'oil', 'car', 'search']):
        print(f"\nScript ({len(sc)} chars):")
        print(sc[:1500])

# Meklē Alpine.js komponentes
print("\n=== Alpine.js x-data ===")
alpine = re.findall(r'x-data=["\']([^"\']{0,800})["\']', html)
for a in alpine[:5]:
    if 'api' in a.lower() or 'url' in a.lower() or 'oww' in a.lower():
        print(f"  {a[:500]}")

# Meklē OWW konfigurācijas JSON
print("\n=== JSON bloki ar oww/vehicle ===")
json_like = re.findall(r'\{[^{}]*(?:oww|vehicle|brand)[^{}]{0,500}\}', html, re.I)
for j in json_like[:5]:
    print(f"  {j[:400]}")

# Pilnāks meklējums pēc API domēna
print("\n=== openapi references ===")
all_openapi = re.findall(r'openapi[^\s"\'<]{3,100}', html)
for o in set(all_openapi[:10]):
    print(f"  {o}")
