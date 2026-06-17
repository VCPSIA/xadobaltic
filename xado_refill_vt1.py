"""
Atkārtoti importē VT1 (vieglās auto) modifikācijas un saderības.
get_or_create — bez dublikātiem, pievieno tikai trūkstošo.
Run: venv\Scripts\python.exe xado_refill_vt1.py
"""
import os, sys, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

import xado_ua_import as imp
from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import VehicleType

UA_VT_ID = 1
vt = VehicleType.objects.get(slug='passenger-cars')
stats = {'new_mods': 0, 'new_compat': 0, 'brands': 0, 'errors': 0}

print(f"=== VT1 refill: {vt.name_lv} ===\n")

resp = imp.post_api('getBrands', {'vehicle_type_id': UA_VT_ID})
brands_raw = [(v, t) for v, t in imp.parse_options(resp.get('html', '')) if v != '0']
print(f"Markas xado.ua: {len(brands_raw)}\n")

for bi, (ua_brand_id, brand_name) in enumerate(brands_raw):
    db_brand = CarBrand.objects.filter(name=brand_name).first()
    if not db_brand:
        continue

    time.sleep(imp.DELAY)
    mresp = imp.post_api('getModels', {'vehicle_type_id': UA_VT_ID, 'vehicle_type_make_id': ua_brand_id})
    if not mresp:
        stats['errors'] += 1
        continue
    models_raw = [(v, t) for v, t in imp.parse_options(mresp.get('html', '')) if v != '0']
    if not models_raw:
        continue

    ua_model_map = {imp.clean_model_name(t): v for v, t in models_raw}
    brand_new_mods = 0

    for db_model in CarModel.objects.filter(brand=db_brand):
        ua_model_id = ua_model_map.get(db_model.name)
        if not ua_model_id:
            continue

        time.sleep(imp.DELAY)
        tresp = imp.post_api('getTypes', {
            'vehicle_type_id': UA_VT_ID,
            'vehicle_type_make_id': ua_brand_id,
            'vehicle_type_make_model_id': ua_model_id,
        })
        if not tresp:
            stats['errors'] += 1
            continue
        mods_raw = [(v, t) for v, t in imp.parse_options(tresp.get('html', '')) if v != '0']

        for mod_ua_id, mod_name in mods_raw:
            engine, fuel, power, yf2, yt2 = imp.parse_mod_attrs(mod_name)
            mod, created = CarModification.objects.get_or_create(
                car_model=db_model, name=mod_name,
                defaults={'engine_volume': engine, 'fuel_type': fuel,
                          'power_hp': power, 'year_from': yf2, 'year_to': yt2,
                          'is_active': True}
            )
            if created:
                stats['new_mods'] += 1
                brand_new_mods += 1

            time.sleep(imp.DELAY)
            presp = imp.post_api('getProducts', {
                'vehicle_type_id': UA_VT_ID,
                'vehicle_type_make_id': ua_brand_id,
                'vehicle_type_make_model_id': ua_model_id,
                'vehicle_type_make_model_type_id': mod_ua_id,
            })
            if not presp:
                continue
            for ua_name, _ in imp.get_engine_products_from_response(presp):
                for lp in imp.match_products(ua_name):
                    _, c = ProductCompatibility.objects.get_or_create(
                        product=lp, modification=mod,
                        defaults={'note_lv': '', 'note_ru': '', 'note_en': '', 'note_de': ''}
                    )
                    if c:
                        stats['new_compat'] += 1

    pct = int((bi + 1) / len(brands_raw) * 100)
    if brand_new_mods > 0:
        print(f"[{pct:3d}%] {brand_name}: +{brand_new_mods} mods, +{stats['new_compat']} sader. kopā", flush=True)
    elif (bi + 1) % 10 == 0:
        print(f"[{pct:3d}%] {brand_name} (nav jaunu)", flush=True)

print(f"\n=== Pabeigts ===")
print(f"  Jaunas modifikacijas: {stats['new_mods']}")
print(f"  Jaunas saderibas:     {stats['new_compat']}")
print(f"  API kludas:           {stats['errors']}")
