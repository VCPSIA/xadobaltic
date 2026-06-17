import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import django; django.setup()

import xado_ua_import as imp
from selector.models import CarBrand, CarModel

mresp = imp.post_api('getModels', {'vehicle_type_id': 1, 'vehicle_type_make_id': '26'})
ua_models = [(v, t, imp.clean_model_name(t)) for v, t in imp.parse_options(mresp.get('html','')) if v != '0']

db_brand = CarBrand.objects.get(name='Audi (EU)')
no_mod_models = list(CarModel.objects.filter(brand=db_brand, modifications__isnull=True).distinct().values_list('name', flat=True))

ua_clean_map = {clean: (uid, raw) for uid, raw, clean in ua_models}

print(f"DB bez modif: {len(no_mod_models)}, xado.ua: {len(ua_models)}")
print()
print("DB modelis -> xado.ua sakritiba:")
for db_name in sorted(no_mod_models):
    match = ua_clean_map.get(db_name)
    if match:
        print(f"  OK  {db_name!r:40} -> uid={match[0]}, raw={match[1]!r}")
    else:
        # Meklē daļēju sakritību
        partial = [(uid, raw, clean) for uid, raw, clean in ua_models if db_name in clean or clean in db_name]
        if partial:
            print(f"  ~   {db_name!r:40} -> dalejа: {partial[0][1]!r}")
        else:
            print(f"  NAV {db_name!r}")
