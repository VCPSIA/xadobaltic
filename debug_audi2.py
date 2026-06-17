import os, sys, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

import xado_ua_import as imp
from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility

db_brand = CarBrand.objects.get(name='Audi (EU)')

# 1. Pārbauda cik tiešam nav modif
no_mod = CarModel.objects.filter(brand=db_brand, modifications__isnull=True).distinct()
print(f"Modeļi ar modifications__isnull=True: {no_mod.count()}")

# 2. Iegūst models_raw no xado.ua
mresp = imp.post_api('getModels', {'vehicle_type_id': 1, 'vehicle_type_make_id': '26'})
models_raw = [(v, t) for v, t in imp.parse_options(mresp.get('html','')) if v != '0']
ua_clean_map = {imp.clean_model_name(t): v for v, t in models_raw}
print(f"xado.ua modeļi: {len(models_raw)}")

# 3. Pievieno PIRMOS 3 trūkstošos tieši
count = 0
for db_model in no_mod[:5]:
    ua_mid = ua_clean_map.get(db_model.name)
    print(f"\nDB: {db_model.name!r} -> ua_mid={ua_mid}")
    if not ua_mid:
        print("  NAV UA MATCH — izlaiž")
        continue

    tresp = imp.post_api('getTypes', {
        'vehicle_type_id': 1,
        'vehicle_type_make_id': '26',
        'vehicle_type_make_model_id': ua_mid,
    })
    mods_raw = [(v,t) for v,t in imp.parse_options(tresp.get('html','') if tresp else '') if v != '0']
    print(f"  getTypes atgrieza: {len(mods_raw)} modifikācijas")

    for mod_ua_id, mod_name in mods_raw[:2]:
        engine, fuel, power, yf2, yt2 = imp.parse_mod_attrs(mod_name)
        mod, created = CarModification.objects.get_or_create(
            car_model=db_model, name=mod_name,
            defaults={'engine_volume': engine, 'fuel_type': fuel,
                      'power_hp': power, 'year_from': yf2, 'year_to': yt2, 'is_active': True}
        )
        print(f"  {'JAUNS' if created else 'ESOŠS'}: {mod_name}")
        count += 1
    time.sleep(0.4)

print(f"\nKopā apstrādāti: {count}")

# Pārbauda rezultātu
after = CarModel.objects.filter(brand=db_brand, modifications__isnull=True).distinct().count()
print(f"Pēc testa bez modif: {after}")
