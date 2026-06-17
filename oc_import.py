# -*- coding: utf-8 -*-
import sys, io, os, re, time, django, requests, urllib3
from pathlib import Path
from urllib.parse import urljoin, quote
from decimal import Decimal

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
django.setup()

from catalog.models import Brand, Product, ProductVolume
from django.utils.text import slugify

urllib3.disable_warnings()

BASE_URL  = 'https://xadobaltic.lv'
ADMIN_URL = BASE_URL + '/admin'
MEDIA_DIR = Path('media/products')
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

s = requests.Session()
s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
s.verify = False

# ── LOGIN ─────────────────────────────────────────────────────────────────────
print('Piesledzos...')
r = s.post(ADMIN_URL + '/index.php?route=common/login',
           data={'username': 'admin', 'password': 'Janis1964', 'user_token': ''})
m = re.search(r'user_token=([a-zA-Z0-9]+)', r.url + r.text)
TOKEN = m.group(1) if m else ''
print(f'Token: {TOKEN[:20]}...' if TOKEN else 'KLUDE: token nav!')
if not TOKEN:
    sys.exit(1)

# ── PRODUKTU ID SARAKSTS ──────────────────────────────────────────────────────
print('\nIegustu produktu sarakstu...')
all_ids = []
page = 1
while True:
    url = f'{ADMIN_URL}/index.php?route=catalog/product&user_token={TOKEN}&page={page}&limit=100'
    r = s.get(url)
    found = list(dict.fromkeys(re.findall(r'product_id=(\d+)', r.text)))
    if not found:
        break
    print(f'  Lapa {page}: {len(found)} produkti')
    all_ids.extend(found)
    # Paarbauda vai ir nakama lapa
    has_next = bool(re.search(r'page=' + str(page + 1), r.text))
    if not has_next:
        break
    page += 1
    time.sleep(0.2)

all_ids = list(dict.fromkeys(all_ids))
print(f'Kopaa produkti: {len(all_ids)}\n')

# ── ATTELA LEJUPIELĀDE ────────────────────────────────────────────────────────
def dl_img(img_path, pid):
    if not img_path:
        return ''
    # Encode ceļu ar Latvijas burtiem
    encoded = quote(img_path, safe='/')
    url = f'{BASE_URL}/image/{encoded}'
    ext = Path(img_path).suffix or '.jpg'
    dest = MEDIA_DIR / f'oc_{pid}{ext}'
    if dest.exists() and dest.stat().st_size > 500:
        return f'products/{dest.name}'
    try:
        r = s.get(url, timeout=20)
        if r.status_code == 200 and len(r.content) > 500:
            dest.write_bytes(r.content)
            return f'products/{dest.name}'
        else:
            print(f'    Attels {r.status_code}: {url[:80]}')
    except Exception as e:
        print(f'    Attels klude: {e}')
    return ''

# ── PRODUKTA DATI NO ADMIN ────────────────────────────────────────────────────
def get_product(pid):
    url = f'{ADMIN_URL}/index.php?route=catalog/product/edit&user_token={TOKEN}&product_id={pid}'
    html = s.get(url).text

    # Nosaukumi pec valodu ID
    names = dict(re.findall(
        r'name="product_description\[(\d+)\]\[name\]"\s+[^>]*value="([^"]*)"', html))

    # Apraksti
    descs_raw = re.findall(
        r'name="product_description\[(\d+)\]\[description\]"[^>]*>(.*?)</textarea>', html, re.S)
    descs = {lid: re.sub(r'<[^>]+>', ' ', d).strip() for lid, d in descs_raw}

    # Cena (name="price")
    pm = re.search(r'name="price"\s+value="([^"]*)"', html)
    try:
        price = Decimal(pm.group(1)).quantize(Decimal('0.01')) if pm else None
    except Exception:
        price = None

    # SKU un modelis
    skm = re.search(r'name="sku"\s+value="([^"]*)"', html)
    mdm = re.search(r'name="model"\s+value="([^"]*)"', html)
    sku   = skm.group(1).strip() if skm else ''
    model = mdm.group(1).strip() if mdm else ''

    # Attels (name="image")
    im = re.search(r'name="image"\s+value="([^"]*)"', html)
    img_path = im.group(1).strip() if im else ''

    # Razotajs (name="manufacturer")
    bm = re.search(r'name="manufacturer"\s+value="([^"]*)"', html)
    brand_name = bm.group(1).strip() if bm else ''

    # Valodas: OpenCart standarts - skatam kas ir DB
    # Tipiski: 1=EN, 2=LV vai RU atkaribaa no instalacijas
    lang_ids = sorted(names.keys(), key=int)
    name_lv = names.get('2', names.get('1', names.get(lang_ids[0], '') if lang_ids else ''))
    name_ru = names.get('3', names.get('2', ''))
    name_en = names.get('1', '')
    # Ja visi valodu ID ir 1,2,3 - LV ir 2, RU=3, EN=1 (tipiska LV opencart)
    # Ja tikai 1 valoda - izmantot visur
    if len(names) == 1:
        name_lv = name_en = name_ru = list(names.values())[0]
    elif len(names) == 3:
        name_lv = names.get('2', '')
        name_ru = names.get('3', '')
        name_en = names.get('1', '')

    desc_lv = descs.get('2', descs.get('1', list(descs.values())[0] if descs else ''))
    desc_ru = descs.get('3', '')
    desc_en = descs.get('1', '')
    if len(descs) == 1:
        desc_lv = desc_en = desc_ru = list(descs.values())[0]
    elif len(descs) == 3:
        desc_lv = descs.get('2', '')
        desc_ru = descs.get('3', '')
        desc_en = descs.get('1', '')

    return {
        'id': pid,
        'name_lv':  name_lv.strip(),
        'name_ru':  name_ru.strip(),
        'name_en':  name_en.strip(),
        'desc_lv':  desc_lv[:5000],
        'desc_ru':  desc_ru[:5000],
        'desc_en':  desc_en[:5000],
        'price':    price,
        'sku':      sku or model or f'OC-{pid}',
        'brand':    brand_name,
        'img_path': img_path,
    }

# ── SAGLABĀ DJANGO ────────────────────────────────────────────────────────────
def save(d):
    name = (d['name_lv'] or d['name_en'] or d['name_ru']).strip()
    if not name:
        print(f'  [Izlaists] pid={d["id"]} - nav nosaukuma')
        return

    # Zimols
    brand = None
    if d['brand']:
        bslug = re.sub(r'[^a-z0-9]+', '-', d['brand'].lower()).strip('-')[:50]
        # Vispirms meginam pec nosaukuma, tad pec slug
        brand = Brand.objects.filter(name=d['brand']).first()
        if not brand:
            brand = Brand.objects.filter(slug=bslug).first()
        if not brand:
            # Ja slug jau ir citam zimolam, pievienosim sufixu
            s2 = bslug
            n2 = 1
            while Brand.objects.filter(slug=s2).exists():
                s2 = f'{bslug}-{n2}'; n2 += 1
            brand = Brand.objects.create(name=d['brand'], slug=s2, is_active=True)

    # Attels
    img_field = dl_img(d['img_path'], d['id'])

    # Slug
    base = slugify(name)[:70] or f'product-{d["id"]}'
    slug = base
    n = 1
    while Product.objects.filter(slug=slug).exists():
        slug = f'{base}-{n}'; n += 1

    sku_val = d['sku'][:100]

    prod, created = Product.objects.update_or_create(
        sku=sku_val,
        defaults=dict(
            slug=slug,
            name_lv=d['name_lv'] or name,
            name_ru=d['name_ru'],
            name_en=d['name_en'],
            description_lv=d['desc_lv'],
            description_ru=d['desc_ru'],
            description_en=d['desc_en'],
            brand=brand,
            price=d['price'],
            image=img_field,
            is_active=True,
        )
    )

    # Cena ka ProductVolume
    if d['price'] and not prod.volumes.exists():
        ProductVolume.objects.create(
            product=prod, label='1 gab.',
            price=d['price'], is_default=True)

    ikona = 'Jauns' if created else 'Atkart'
    att   = ' [foto]' if img_field else ''
    print(f'  [{ikona}]{att} {name[:60]} — {d["price"]} EUR | {d["brand"]}')

# ── MAIN ──────────────────────────────────────────────────────────────────────
print(f'Importeju {len(all_ids)} produktus...\n')
# Dzesam vecos (OC-*) lai varam atjaunot
Product.objects.filter(sku__startswith='OC-').delete()

ok = 0
for pid in all_ids:
    try:
        data = get_product(pid)
        save(data)
        ok += 1
    except Exception as e:
        print(f'  [Klude] pid={pid}: {e}')
    time.sleep(0.2)

print(f'\nGatavs! Importeti: {ok}/{len(all_ids)} produkti')
from catalog.models import Product as P
print(f'Ar attelu: {P.objects.exclude(image="").count()}')
print(f'Ar zīmolu: {P.objects.exclude(brand=None).count()}')
