# -*- coding: utf-8 -*-
import sys, io, os, re, time, csv, django, requests, urllib3
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
django.setup()

urllib3.disable_warnings()

BASE_URL  = 'https://xadobaltic.lv'
ADMIN_URL = BASE_URL + '/admin'
OUT_FILE  = 'klienti.csv'

s = requests.Session()
s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
s.verify = False

# ── PIESLĒGŠANĀS ──────────────────────────────────────────────────────────────
print('Piesledzos...')
r = s.post(ADMIN_URL + '/index.php?route=common/login',
           data={'username': 'admin', 'password': 'Janis1964', 'user_token': ''})
m = re.search(r'user_token=([a-zA-Z0-9]+)', r.url + r.text)
TOKEN = m.group(1) if m else ''
print(f'Token: {TOKEN[:20]}...' if TOKEN else 'KLUDE: token nav!')
if not TOKEN:
    sys.exit(1)

# ── KLIENTU ID SARAKSTS ───────────────────────────────────────────────────────
print('\nIegustu klientu sarakstu...')
all_ids = []
page = 1
while True:
    url = f'{ADMIN_URL}/index.php?route=customer/customer&user_token={TOKEN}&page={page}'
    r = s.get(url)
    # Meklē customer_id saites
    found = list(dict.fromkeys(re.findall(r'customer_id=(\d+)', r.text)))
    if not found:
        break
    print(f'  Lapa {page}: {len(found)} klienti')
    all_ids.extend(found)
    has_next = bool(re.search(r'page=' + str(page + 1), r.text))
    if not has_next:
        break
    page += 1
    time.sleep(0.3)

all_ids = list(dict.fromkeys(all_ids))
print(f'Kopaa klienti: {len(all_ids)}\n')

if not all_ids:
    print('Nav klientu! Parbaudam tabulas datus tiesak...')
    # Megina izvelkt no saraksta tabulas tiesak (bez individualam lapam)
    url = f'{ADMIN_URL}/index.php?route=customer/customer&user_token={TOKEN}'
    r = s.get(url)
    # Saglaba HTML debugam
    Path('debug_customers.html').write_text(r.text, encoding='utf-8')
    print('HTML saglabats: debug_customers.html')
    sys.exit(1)

# ── KLIENTA DATI ──────────────────────────────────────────────────────────────
def get_customer(cid):
    url = f'{ADMIN_URL}/index.php?route=customer/customer/edit&user_token={TOKEN}&customer_id={cid}'
    html = s.get(url).text

    def val(name):
        m = re.search(rf'name=["\'](?:customer\[)?{name}(?:\])?["\'][^>]*value=["\']([^"\']*)["\']', html)
        if m: return m.group(1).strip()
        m = re.search(rf'id=["\']input-{name}["\'][^>]*value=["\']([^"\']*)["\']', html)
        return m.group(1).strip() if m else ''

    firstname = val('firstname')
    lastname  = val('lastname')
    email     = val('email')
    phone     = val('telephone')
    # Mekle ari cita veida tālruņa laukus
    if not phone:
        m = re.search(r'name=["\']telephone["\'][^>]*value=["\']([^"\']*)["\']', html)
        phone = m.group(1).strip() if m else ''

    # Adrese no pirmā address bloka
    def addr_val(name):
        m = re.search(rf'name=["\']address(?:_\d+)?\[{name}\]["\'][^>]*value=["\']([^"\']*)["\']', html)
        if m: return m.group(1).strip()
        m = re.search(rf'name=["\']address\[\d+\]\[{name}\]["\'][^>]*value=["\']([^"\']*)["\']', html)
        return m.group(1).strip() if m else ''

    address1  = addr_val('address_1')
    address2  = addr_val('address_2')
    city      = addr_val('city')
    postcode  = addr_val('postcode')
    company   = addr_val('company')

    # Pasūtījumu skaits
    orders_m = re.search(r'orders.*?(\d+)', html[:500], re.I)
    orders = orders_m.group(1) if orders_m else '0'

    # Reģistrācijas datums
    date_m = re.search(r'date_added.*?value=["\']([^"\']+)["\']', html)
    reg_date = date_m.group(1) if date_m else ''

    return {
        'id':       cid,
        'vards':    firstname,
        'uzvards':  lastname,
        'epasts':   email,
        'talrunis': phone,
        'uznemums': company,
        'adrese':   address1,
        'adrese2':  address2,
        'pilseta':  city,
        'pasta_indekss': postcode,
        'registrets': reg_date,
    }

# ── GALVENĀ CILPA ─────────────────────────────────────────────────────────────
print(f'Apstradaju {len(all_ids)} klientus...\n')
klienti = []
for i, cid in enumerate(all_ids, 1):
    try:
        d = get_customer(cid)
        klienti.append(d)
        print(f'  [{i}/{len(all_ids)}] {d["vards"]} {d["uzvards"]} | {d["epasts"]} | {d["talrunis"]}')
    except Exception as e:
        print(f'  [Klude] id={cid}: {e}')
    time.sleep(0.2)

# ── CSV EKSPORTS ──────────────────────────────────────────────────────────────
if klienti:
    lauki = ['id','vards','uzvards','epasts','talrunis','uznemums',
             'adrese','adrese2','pilseta','pasta_indekss','registrets']
    with open(OUT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=lauki)
        w.writeheader()
        w.writerows(klienti)
    print(f'\nGatavs! {len(klienti)} klienti saglabati: {OUT_FILE}')
    # Statistika
    ar_email   = sum(1 for k in klienti if k['epasts'])
    ar_talruni = sum(1 for k in klienti if k['talrunis'])
    ar_adresi  = sum(1 for k in klienti if k['adrese'])
    print(f'  Ar e-pastu:  {ar_email}')
    print(f'  Ar talruni: {ar_talruni}')
    print(f'  Ar adresi:  {ar_adresi}')
else:
    print('Nav datu!')
