"""
Importē tikai trūkstošos datus:
  - VT4 (Motocikli) — 0 markas, pilns imports
  - VT5 (Lauksaimniecība) — 0 markas, pilns imports
  - VT1 (Vieglās auto) — tikai markas kuras VĒL NAV datubāzē (T-Z un citas)

Run: venv\Scripts\python.exe xado_import_missing.py
"""

import os, sys, time
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

import xado_ua_import as imp
from selector.models import CarBrand
from catalog.models import VehicleType

def import_vt(ua_vt_id, vt_obj, existing_brand_names=None):
    """Imports one vehicle type. If existing_brand_names given, skips those brands."""
    stats = {'brands': 0, 'models': 0, 'mods': 0, 'compat': 0, 'skipped': 0}

    resp = imp.post_api('getBrands', {'vehicle_type_id': ua_vt_id})
    if not resp:
        print(f'  ! getBrands kļūda VT{ua_vt_id}')
        return stats

    brands_raw = [(v, t) for v, t in imp.parse_options(resp.get('html', '')) if v != '0']
    print(f'  xado.ua atgrieza {len(brands_raw)} markas')

    skipped_brands = 0
    for bi, (brand_ua_id, brand_name) in enumerate(brands_raw):
        # Skip already fully imported brands (for VT1 partial reimport)
        if existing_brand_names and brand_name in existing_brand_names:
            skipped_brands += 1
            continue

        brand, created = CarBrand.objects.get_or_create(
            name=brand_name,
            defaults={'slug': imp.make_slug(brand_name), 'is_active': True}
        )
        if created:
            stats['brands'] += 1
        if not brand.vehicle_types.filter(id=vt_obj.id).exists():
            brand.vehicle_types.add(vt_obj)

        time.sleep(imp.DELAY)
        mresp = imp.post_api('getModels', {'vehicle_type_id': ua_vt_id, 'vehicle_type_make_id': brand_ua_id})
        if not mresp:
            continue
        models_raw = [(v, t) for v, t in imp.parse_options(mresp.get('html', '')) if v != '0']
        if not models_raw:
            continue

        for model_ua_id, model_raw in models_raw:
            clean_name = imp.clean_model_name(model_raw)
            yf, yt = imp.parse_year_range(model_raw)
            model, m_created = imp.CarModel.objects.get_or_create(
                brand=brand, name=clean_name,
                defaults={'vehicle_type': vt_obj, 'year_from': yf, 'year_to': yt, 'is_active': True}
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

            for mod_ua_id, mod_name in mods_raw:
                engine, fuel, power, yf2, yt2 = imp.parse_mod_attrs(mod_name)
                mod, mod_created = imp.CarModification.objects.get_or_create(
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
                for ua_name, system_name in imp.get_engine_products_from_response(presp):
                    local_prods = imp.match_products(ua_name)
                    if not local_prods:
                        stats['skipped'] += 1
                        continue
                    for lp in local_prods:
                        _, c_created = imp.ProductCompatibility.objects.get_or_create(
                            product=lp, modification=mod,
                            defaults={'note_lv': '', 'note_ru': '', 'note_en': '', 'note_de': ''}
                        )
                        if c_created:
                            stats['compat'] += 1

        pct = int((bi + 1) / max(len(brands_raw), 1) * 100)
        print(f'  [{pct:3d}%] {brand_name}: +{stats["models"]} modeļi, +{stats["compat"]} saderības', flush=True)

    if skipped_brands:
        print(f'  (izlaistas {skipped_brands} jau importētas markas)')
    return stats


def run():
    print('=== XADO Import — trūkstošie dati ===\n')

    # VT1: Vieglās automašīnas — pievieno tikai jaunas markas
    vt1 = VehicleType.objects.get(slug='passenger-cars')
    existing_vt1_brands = set(CarBrand.objects.filter(vehicle_types=vt1).values_list('name', flat=True))
    print(f'\n── VT1: {vt1.name_lv} (jau importētas: {len(existing_vt1_brands)} markas) ──')
    s1 = import_vt(1, vt1, existing_brand_names=existing_vt1_brands)
    print(f'  +{s1["brands"]} markas, +{s1["models"]} modeļi, +{s1["mods"]} mods, +{s1["compat"]} saderības')

    # VT4: Motocikli
    vt4 = VehicleType.objects.get(slug='motorcycle')
    print(f'\n── VT4: {vt4.name_lv} ──')
    s4 = import_vt(4, vt4)
    print(f'  +{s4["brands"]} markas, +{s4["models"]} modeļi, +{s4["mods"]} mods, +{s4["compat"]} saderības')

    # VT5: Lauksaimniecība
    vt5 = VehicleType.objects.get(slug='agricultural')
    print(f'\n── VT5: {vt5.name_lv} ──')
    s5 = import_vt(5, vt5)
    print(f'  +{s5["brands"]} markas, +{s5["models"]} modeļi, +{s5["mods"]} mods, +{s5["compat"]} saderības')

    print('\n=== Pabeigts ===')


if __name__ == '__main__':
    run()
