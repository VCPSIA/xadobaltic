"""
Fills missing models for brands that were imported but got 0 models (API throttle).
Run: venv\Scripts\python.exe xado_fill_models.py
"""
import os, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django
django.setup()

import xado_ua_import as imp
from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import VehicleType

DELAY = 0.8  # longer delay to avoid throttling

# xado_vt_id -> our DB VehicleType id
VT_MAP = {1: 5, 2: 6, 3: 7}


def fill_vt(xado_vt_id, db_vt_id):
    vt = VehicleType.objects.get(id=db_vt_id)
    missing = CarBrand.objects.filter(
        vehicle_types=vt, is_active=True
    ).exclude(models__is_active=True).distinct()

    total_missing = missing.count()
    if total_missing == 0:
        print(f'  vt={db_vt_id} ({vt.name_lv}): nav trukstoso, izlaiz')
        return

    print(f'\n== vt={db_vt_id} ({vt.name_lv}): {total_missing} markas bez modeliem ==')

    # Get brand list from API to find xado brand IDs
    resp = imp.post_api('getBrands', {'vehicle_type_id': xado_vt_id})
    if not resp:
        print('  ! getBrands API kludа')
        return

    api_brands = {name: uid for uid, name in imp.parse_options(resp.get('html', '')) if uid != '0'}
    print(f'  API atgriezas {len(api_brands)} markas')

    stats = {'models': 0, 'mods': 0, 'compat': 0, 'skipped': 0, 'no_api_id': 0}

    for bi, brand in enumerate(missing):
        brand_ua_id = api_brands.get(brand.name)
        if not brand_ua_id:
            stats['no_api_id'] += 1
            continue

        time.sleep(DELAY)
        mresp = imp.post_api('getModels', {'vehicle_type_id': xado_vt_id, 'vehicle_type_make_id': brand_ua_id})
        if not mresp:
            continue
        models_raw = [(v, t) for v, t in imp.parse_options(mresp.get('html', '')) if v != '0']
        if not models_raw:
            continue

        for model_ua_id, model_raw in models_raw[:imp.MAX_MODELS]:
            clean_name = imp.clean_model_name(model_raw)
            yf, yt = imp.parse_year_range(model_raw)
            model, m_created = CarModel.objects.get_or_create(
                brand=brand, name=clean_name,
                defaults={'vehicle_type': vt, 'year_from': yf, 'year_to': yt, 'is_active': True}
            )
            if m_created:
                stats['models'] += 1

            time.sleep(DELAY)
            tresp = imp.post_api('getTypes', {
                'vehicle_type_id': xado_vt_id,
                'vehicle_type_make_id': brand_ua_id,
                'vehicle_type_make_model_id': model_ua_id,
            })
            if not tresp:
                continue
            mods_raw = [(v, t) for v, t in imp.parse_options(tresp.get('html', '')) if v != '0']

            for mod_ua_id, mod_name in mods_raw[:imp.MAX_MODS]:
                engine, fuel, power, yf2, yt2 = imp.parse_mod_attrs(mod_name)
                mod, mod_created = CarModification.objects.get_or_create(
                    car_model=model, name=mod_name,
                    defaults={
                        'engine_volume': engine, 'fuel_type': fuel,
                        'power_hp': power, 'year_from': yf2, 'year_to': yt2,
                        'is_active': True,
                    }
                )
                if mod_created:
                    stats['mods'] += 1

                time.sleep(DELAY)
                presp = imp.post_api('getProducts', {
                    'vehicle_type_id': xado_vt_id,
                    'vehicle_type_make_id': brand_ua_id,
                    'vehicle_type_make_model_id': model_ua_id,
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
                            stats['compat'] += 1
                    if not imp.match_products(ua_name):
                        stats['skipped'] += 1

        pct = int((bi + 1) / total_missing * 100)
        print(f'  [{pct:3d}%] {brand.name}: +{stats["models"]} modeli, +{stats["compat"]} saderibas')

    print(f'  Jauni modeli: {stats["models"]}, mods: {stats["mods"]}, saderibas: {stats["compat"]}')
    print(f'  Nav API ID: {stats["no_api_id"]}')


def main():
    print('=== Fill missing models ===')
    imp.DELAY = DELAY
    for xado_id, db_id in VT_MAP.items():
        fill_vt(xado_id, db_id)
    print('\n=== Pabeigts ===')


if __name__ == '__main__':
    main()
