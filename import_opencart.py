"""
OpenCart → Django importēšanas skripts.
Piesakās xadobaltic.lv/admin, eksportē produktus un importē Django.
Palaid: venv\Scripts\python.exe import_opencart.py
"""
import os, sys, re, time, json
import django
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse

# ── Django setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
django.setup()

from catalog.models import Brand, Category, Product, ProductVolume
from decimal import Decimal

# ── Konfigurācija ─────────────────────────────────────────────────────────────
BASE_URL   = 'https://xadobaltic.lv'
ADMIN_URL  = BASE_URL + '/admin'
USERNAME   = 'admin'
PASSWORD   = 'Janis1964'
MEDIA_DIR  = Path(__file__).parent / 'media' / 'products'
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'lv,en;q=0.9',
}

session = requests.Session()
session.headers.update(HEADERS)
session.verify = False  # ignorē SSL kļūdas ja ir

import urllib3
urllib3.disable_warnings()

# ══════════════════════════════════════════════════════════════════════════════
# 1. PIESLĒGŠANĀS ADMIN PANELIM
# ══════════════════════════════════════════════════════════════════════════════
def login():
    print('→ Pieslēdzos admin panelim...')
    r = session.get(ADMIN_URL + '/index.php?route=common/login')
    # Meklē token vai user_token
    token_match = re.search(r'name=["\']user_token["\'] value=["\']([^"\']+)["\']', r.text)
    token = token_match.group(1) if token_match else ''

    data = {
        'username': USERNAME,
        'password': PASSWORD,
        'user_token': token,
    }
    r2 = session.post(ADMIN_URL + '/index.php?route=common/login', data=data)

    if 'dashboard' in r2.url or 'route=common/dashboard' in r2.text or 'logout' in r2.text.lower():
        print('✓ Pieslēgšanās veiksmīga!')
        # Izvelk user_token no URL vai lapas
        m = re.search(r'user_token=([a-f0-9]+)', r2.url + r2.text)
        return m.group(1) if m else ''
    else:
        print('✗ Neizdevās pieslēgties. Pārbaudi paroli.')
        print('  URL:', r2.url)
        sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# 2. PRODUKTU SARAKSTA IEGŪŠANA
# ══════════════════════════════════════════════════════════════════════════════
def get_all_product_ids(token):
    print('\n→ Iegūstu produktu sarakstu...')
    ids = []
    page = 1
    while True:
        url = (f'{ADMIN_URL}/index.php?route=catalog/product&user_token={token}'
               f'&page={page}&limit=100')
        r = session.get(url)
        # Meklē produktu ID no labošanas saitēm
        found = re.findall(r'route=catalog/product/edit[^"\']*product_id=(\d+)', r.text)
        if not found:
            break
        ids.extend(found)
        print(f'  Lapa {page}: {len(found)} produkti')
        # Pārbauda vai ir nākamā lapa
        if f'page={page+1}' not in r.text and 'Next' not in r.text:
            break
        page += 1
        time.sleep(0.3)
    # Noņem duplikātus
    ids = list(dict.fromkeys(ids))
    print(f'✓ Kopā produkti: {len(ids)}')
    return ids

# ══════════════════════════════════════════════════════════════════════════════
# 3. VIENA PRODUKTA DATU IEGŪŠANA
# ══════════════════════════════════════════════════════════════════════════════
def get_product_data(product_id, token):
    url = f'{ADMIN_URL}/index.php?route=catalog/product/edit&user_token={token}&product_id={product_id}'
    r = session.get(url)
    html = r.text

    def field(name):
        m = re.search(rf'name=["\']product\[{name}\]["\'][^>]*value=["\']([^"\']*)["\']', html)
        if m:
            return m.group(1).strip()
        m = re.search(rf'id=["\']input-{name}["\'][^>]*value=["\']([^"\']*)["\']', html)
        return m.group(1).strip() if m else ''

    def textarea(name):
        m = re.search(rf'name=["\']product\[{name}\]["\'][^>]*>(.*?)</textarea>', html, re.S)
        return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''

    # Nosaukumi dažādās valodās (OpenCart izmanto language_id)
    # LV=4 (vai 1), RU=8 (vai 2), EN=1 (vai 3)
    names = {}
    descs = {}
    for lang_label, patterns in [('lv', [r'language_id.*?4', r'language_id.*?1']),
                                   ('ru', [r'language_id.*?8', r'language_id.*?2']),
                                   ('en', [r'language_id.*?3', r'language_id.*?1'])]:
        m = re.search(
            r'name=["\']product_description\[\d+\]\[name\]["\'][^>]*value=["\']([^"\']*)["\']',
            html)
        if m:
            names[lang_label] = m.group(1)

    # Visi nosaukumi no formas
    all_names = re.findall(
        r'name=["\']product_description\[(\d+)\]\[name\]["\'][^>]*value=["\']([^"\']*)["\']', html)
    all_descs = re.findall(
        r'name=["\']product_description\[(\d+)\]\[description\]["\'][^>]*>(.*?)</textarea>',
        html, re.S)

    name_map = {lid: n for lid, n in all_names}
    desc_map = {lid: re.sub(r'<[^>]+>', '', d).strip() for lid, d in all_descs}

    # Cena
    price_raw = field('price')
    try:
        price = Decimal(price_raw.replace(',', '.')) if price_raw else None
    except Exception:
        price = None

    # Attēli
    main_img = re.search(r'id=["\']thumb-image["\'][^>]*src=["\']([^"\']+)["\']', html)
    if not main_img:
        main_img = re.search(r'name=["\']product\[image\]["\'][^>]*value=["\']([^"\']*)["\']', html)
    main_image_url = main_img.group(1) if main_img else ''

    extra_imgs = re.findall(
        r'name=["\']product_image\[\d+\]\[image\]["\'][^>]*value=["\']([^"\']+)["\']', html)

    # SKU / modelis
    model = field('model')
    sku = field('sku')

    # Kategorija
    cat_ids = re.findall(r'name=["\']product_category\[\].*?value=["\'](\d+)["\'].*?selected', html)
    if not cat_ids:
        cat_ids = re.findall(r"'product_category'\s*:\s*\[([^\]]*)\]", html)

    # Zīmols/ražotājs
    mfr_match = re.search(r'name=["\']manufacturer_id["\'][^>]*>.*?<option[^>]*selected[^>]*value=["\'](\d+)["\'].*?>(.*?)</option>', html, re.S)
    brand_name = ''
    if mfr_match:
        brand_name = mfr_match.group(2).strip()
    else:
        m = re.search(r'id=["\']input-manufacturer["\'][^>]*value=["\']([^"\']+)["\']', html)
        brand_name = m.group(1) if m else ''

    # Pirmais nosaukums kas pieejams
    name_lv = name_map.get('4', name_map.get('1', next(iter(name_map.values()), ''))) if name_map else ''
    name_ru = name_map.get('8', name_map.get('2', '')) if name_map else ''
    name_en = name_map.get('3', '') if name_map else ''

    desc_lv = desc_map.get('4', desc_map.get('1', next(iter(desc_map.values()), ''))) if desc_map else ''
    desc_ru = desc_map.get('8', desc_map.get('2', '')) if desc_map else ''
    desc_en = desc_map.get('3', '') if desc_map else ''

    return {
        'id': product_id,
        'name_lv': name_lv,
        'name_ru': name_ru,
        'name_en': name_en,
        'desc_lv': desc_lv,
        'desc_ru': desc_ru,
        'desc_en': desc_en,
        'price': price,
        'model': model,
        'sku': sku or model,
        'brand': brand_name,
        'image': main_image_url,
        'extra_images': extra_imgs,
    }

# ══════════════════════════════════════════════════════════════════════════════
# 4. ATTĒLA LEJUPIELĀDE
# ══════════════════════════════════════════════════════════════════════════════
def download_image(url, filename):
    if not url:
        return ''
    if not url.startswith('http'):
        url = urljoin(BASE_URL, url)
    # Noņem ?cache= parametrus
    url_clean = url.split('?')[0]
    dest = MEDIA_DIR / filename
    if dest.exists():
        return f'products/{filename}'
    try:
        r = session.get(url_clean, timeout=15)
        if r.status_code == 200 and len(r.content) > 500:
            dest.write_bytes(r.content)
            return f'products/{filename}'
    except Exception as e:
        print(f'    ! Attēls nelejupielādēts: {e}')
    return ''

# ══════════════════════════════════════════════════════════════════════════════
# 5. IMPORTĒŠANA DJANGO
# ══════════════════════════════════════════════════════════════════════════════
def import_product(data):
    name = data['name_lv'] or data['name_en'] or f"Produkts #{data['id']}"
    if not name.strip():
        return None

    # Zīmols
    brand = None
    if data['brand']:
        brand, _ = Brand.objects.get_or_create(
            name=data['brand'],
            defaults={'slug': re.sub(r'[^a-z0-9]+', '-', data['brand'].lower()).strip('-')}
        )

    # Attēls
    img_filename = ''
    if data['image']:
        ext = Path(data['image'].split('?')[0]).suffix or '.jpg'
        img_filename = download_image(data['image'], f"oc_{data['id']}{ext}")

    # Produkts
    from django.utils.text import slugify
    base_slug = slugify(name)[:80] or f'product-{data["id"]}'
    slug = base_slug
    n = 1
    while Product.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{n}'
        n += 1

    product, created = Product.objects.update_or_create(
        sku=data['sku'] if data['sku'] else f'OC-{data["id"]}',
        defaults={
            'slug': slug,
            'name_lv': name,
            'name_ru': data['name_ru'],
            'name_en': data['name_en'],
            'description_lv': data['desc_lv'],
            'description_ru': data['desc_ru'],
            'description_en': data['desc_en'],
            'brand': brand,
            'price': data['price'],
            'image': img_filename,
            'is_active': True,
        }
    )

    # Cena kā ProductVolume
    if data['price'] and not product.volumes.exists():
        ProductVolume.objects.create(
            product=product,
            label='1 gab.',
            price=data['price'],
            is_default=True,
        )

    action = 'Izveidots' if created else 'Atjaunots'
    print(f'  {action}: {name[:60]}')
    return product

# ══════════════════════════════════════════════════════════════════════════════
# GALVENĀ PROGRAMMA
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('=' * 60)
    print('OpenCart → Django importēšana')
    print('=' * 60)

    token = login()
    product_ids = get_all_product_ids(token)

    if not product_ids:
        print('\n✗ Produkti nav atrasti. Iespējams, HTML struktūra atšķiras.')
        print('  Mēģināt CSV eksportu: palaid ar --csv opciju.')
        sys.exit(1)

    print(f'\n→ Importēju {len(product_ids)} produktus...\n')
    ok, fail = 0, 0
    for pid in product_ids:
        try:
            data = get_product_data(pid, token)
            if import_product(data):
                ok += 1
            else:
                fail += 1
        except Exception as e:
            print(f'  ✗ Kļūda produktam {pid}: {e}')
            fail += 1
        time.sleep(0.2)

    print('\n' + '=' * 60)
    print(f'✓ Importēti: {ok} produkti')
    if fail:
        print(f'✗ Kļūdas: {fail}')
    print('=' * 60)
