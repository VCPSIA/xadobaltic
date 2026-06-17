"""
Imports missing vehicle types (xado id=3,4,5) from xado.ua.
Run: venv\Scripts\python.exe xado_missing_vt.py
"""
import os, sys, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

import xado_ua_import as imp
from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility

MISSING_VT_IDS = [3, 4, 5]  # Smagais kravas, Motocikls, Lauksaimn. tehnika


def run_vt(ua_vt_id, vt, stats):
    print(f'\n-- {vt.name_lv} (xado id={ua_vt_id}) --')

    resp = imp.post_api('getBrands', {'vehicle_type_id': ua_vt_id})
    if not resp:
        print('  ! getBrands kļūda')
        return

    brands_raw = [(v, t) for v, t in imp.parse_options(resp.get('html', '')) if v != '0']
    print(f'  Markas: {len(brands_raw)}')
    if not brands_raw:
        print('  ! Nav marku')
        return

    for bi, (brand_ua_id, brand_name) in enumerate(brands_raw[:imp.MAX_BRANDS]):
        brand, created = CarBrand.objects.get_or_create(
            name=brand_name,
            defaults={'slug': imp.make_slug(brand_name), 'is_active': True}
        )
        if created:
            stats['brands'] += 1
        if not brand.vehicle_types.filter(id=vt.id).exists():
            brand.vehicle_types.add(vt)

        time.sleep(imp.DELAY)
        mresp = imp.post_api('getModels', {'vehicle_type_id': ua_vt_id, 'vehicle_type_make_id': brand_ua_id})
        if not mresp:
            continue
        models_raw = [(v, t) for v, t in imp.parse_options(mresp.get('html', '')) if v != '0']
        if not models_raw:
            continue

        for mi, (model_ua_id, model_raw) in enumerate(models_raw[:imp.MAX_MODELS]):
            clean_name = imp.clean_model_name(model_raw)
            yf, yt = imp.parse_year_range(model_raw)
            model, m_created = CarModel.objects.get_or_create(
                brand=brand, name=clean_name,
                defaults={'vehicle_type': vt, 'year_from': yf, 'year_to': yt, 'is_active': True}
            )
            if m_created:
                stats['models'] += 1

            time.sleep(imp.DELAY)
            tresp = imp.post_api('getTypes', {
                'vehicle_type_id': ua_vt_id,
                'vehicle_type_make_id': brand_ua_id,
                'vehicle_type_make_model_id': model_ua_id,
            })
            if not tresp:
                continue
            mods_raw = [(v, t) for v, t in imp.parse_options(tresp.get('html', '')) if v != '0']
            if not mods_raw:
                continue

            for ti, (mod_ua_id, mod_name) in enumerate(mods_raw[:imp.MAX_MODS]):
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

                time.sleep(imp.DELAY)
                presp = imp.post_api('getProducts', {
                    'vehicle_type_id': ua_vt_id,
                    'vehicle_type_make_id': brand_ua_id,
                    'vehicle_type_make_model_id': model_ua_id,
                    'vehicle_type_make_model_type_id': mod_ua_id,
                })
                if not presp:
                    continue

                ua_products = imp.get_engine_products_from_response(presp)
                for ua_name, system_name in ua_products:
                    local_prods = imp.match_products(ua_name)
                    if not local_prods:
                        stats['skipped'] += 1
                        continue
                    for lp in local_prods:
                        _, c_created = ProductCompatibility.objects.get_or_create(
                            product=lp, modification=mod,
                            defaults={'note_lv': '', 'note_ru': '', 'note_en': '', 'note_de': ''}
                        )
                        if c_created:
                            stats['compat'] += 1

        pct = int((bi + 1) / max(len(brands_raw), 1) * 100)
        print(f'  [{pct:3d}%] {brand_name}: {len(models_raw)} modeli, '
              f'{stats["mods"]} mods kopa, {stats["compat"]} saderibas')


def main():
    print('=== Trūkstošo VT imports sākts ===')
    stats = {'brands': 0, 'models': 0, 'mods': 0, 'compat': 0, 'skipped': 0}

    vt_map = imp.ensure_vehicle_types()

    for ua_vt_id in MISSING_VT_IDS:
        vt = vt_map.get(ua_vt_id)
        if vt:
            run_vt(ua_vt_id, vt, stats)

    print(f'\n=== Importēts ===')
    print(f'  Jaunas markas:        {stats["brands"]}')
    print(f'  Jauni modeļi:         {stats["models"]}')
    print(f'  Jaunas modifikācijas: {stats["mods"]}')
    print(f'  Saderības ieraksti:   {stats["compat"]}')
    print(f'  Nesaskaņoti produkti: {stats["skipped"]}')


if __name__ == '__main__':
    main()
