"""
Demo datu ievietošana xadobaltic projektā
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import SiteSettings, Banner
from catalog.models import Brand, Category, VehicleType, Product
from selector.models import CarBrand, CarModel, CarModification, ProductCompatibility

print("Izveido superuser...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@xadobaltic.lv', 'admin123')
    print("  admin / admin123")
else:
    print("  (jau eksistē)")

print("Vietnes iestatījumi...")
settings = SiteSettings.get()
settings.phone = '+371 20 000 000'
settings.email = 'info@xadobaltic.lv'
settings.address_lv = 'Rīga, Latvija'
settings.address_ru = 'Рига, Латвия'
settings.address_en = 'Riga, Latvia'
settings.address_de = 'Riga, Lettland'
settings.save()

print("Baneri...")
if not Banner.objects.exists():
    Banner.objects.create(
        title_lv='Augstas kvalitātes XADO eļļas',
        title_ru='Высококачественные масла XADO',
        title_en='High-quality XADO oils',
        title_de='Hochwertige XADO Öle',
        subtitle_lv='Revitalizants tehnoloģija — dzinēja atjaunošana un aizsardzība',
        subtitle_ru='Технология ревитализант — восстановление и защита двигателя',
        subtitle_en='Revitalizant technology — engine restoration and protection',
        subtitle_de='Revitalizant-Technologie — Motorwiederherstellung und -schutz',
        button_text_lv='Skatīt katalogs',
        button_text_ru='Просмотреть каталог',
        button_text_en='View catalog',
        button_text_de='Katalog ansehen',
        button_url='/catalog/',
        order=1,
    )
    Banner.objects.create(
        title_lv='Atlasīt eļļu pēc jūsu automašīnas',
        title_ru='Подобрать масло по вашему автомобилю',
        title_en='Find oil for your car',
        title_de='Öl für Ihr Auto finden',
        subtitle_lv='Vienkārša meklēšana pēc markas, modeļa un modifikācijas',
        subtitle_ru='Простой поиск по марке, модели и модификации',
        subtitle_en='Easy search by brand, model and modification',
        subtitle_de='Einfache Suche nach Marke, Modell und Modifikation',
        button_text_lv='Atlasīt tagad',
        button_text_ru='Подобрать сейчас',
        button_text_en='Select now',
        button_text_de='Jetzt auswählen',
        button_url='/selector/',
        order=2,
    )

print("Zīmoli...")
brands = {}
brand_data = [
    ('XADO', 'xado'),
    ('RED BOOST', 'red-boost'),
    ('ATOMEX', 'atomex'),
    ('VERYLUBE', 'verylube'),
]
for name, slug in brand_data:
    b, _ = Brand.objects.get_or_create(slug=slug, defaults={'name': name})
    brands[slug] = b
    print(f"  {name}")

print("Transportlīdzekļu tipi...")
vt_data = [
    ('Vieglā automašīna', 'Легковой автомобиль', 'Passenger car', 'PKW', 'car', 'bi-car-front'),
    ('SUV / Džips', 'Внедорожник / Джип', 'SUV / Jeep', 'SUV / Geländewagen', 'suv', 'bi-truck'),
    ('Kravas auto', 'Грузовик', 'Truck', 'LKW', 'truck', 'bi-truck-flatbed'),
    ('Motocikls', 'Мотоцикл', 'Motorcycle', 'Motorrad', 'motorcycle', 'bi-bicycle'),
]
vehicle_types = {}
for lv, ru, en, de, slug, icon in vt_data:
    vt, _ = VehicleType.objects.get_or_create(slug=slug, defaults={
        'name_lv': lv, 'name_ru': ru, 'name_en': en, 'name_de': de, 'icon': icon
    })
    vehicle_types[slug] = vt

print("Kategorijas...")
cat_data = [
    ('Motoreļļas', 'Моторные масла', 'Motor oils', 'Motoröle', 'motor-oils', 'bi-droplet-fill'),
    ('Piedevas', 'Присадки', 'Additives', 'Additive', 'additives', 'bi-plus-circle'),
    ('Transmisiju eļļas', 'Трансмиссионные масла', 'Transmission oils', 'Getriebeöle', 'transmission-oils', 'bi-gear'),
    ('Hidraulikas eļļas', 'Гидравлические масла', 'Hydraulic oils', 'Hydrauliköle', 'hydraulic-oils', 'bi-wrench'),
    ('Autoķīmija', 'Автохимия', 'Auto chemistry', 'Autochemie', 'auto-chemistry', 'bi-droplet'),
    ('Autokosmētika', 'Автокосметика', 'Auto cosmetics', 'Autokosmetik', 'auto-cosmetics', 'bi-stars'),
    ('Remontpiedevas', 'Ремонтные присадки', 'Repair additives', 'Reparaturadditive', 'repair-additives', 'bi-tools'),
    ('Dzesēšanas šķidrumi', 'Охлаждающие жидкости', 'Coolants', 'Kühlmittel', 'coolants', 'bi-thermometer'),
]
categories = {}
for lv, ru, en, de, slug, icon in cat_data:
    cat, _ = Category.objects.get_or_create(slug=slug, defaults={
        'name_lv': lv, 'name_ru': ru, 'name_en': en, 'name_de': de, 'icon': icon
    })
    categories[slug] = cat
    print(f"  {lv}")

print("Produkti...")
products_data = [
    {
        'name_lv': 'XADO 5W-40 Synthetic Motor Oil SN/CF 1L',
        'name_ru': 'XADO 5W-40 Синтетическое моторное масло SN/CF 1L',
        'name_en': 'XADO 5W-40 Synthetic Motor Oil SN/CF 1L',
        'name_de': 'XADO 5W-40 Synthetisches Motoröl SN/CF 1L',
        'slug': 'xado-5w40-synthetic-1l',
        'brand': brands['xado'],
        'category': categories['motor-oils'],
        'price': 18.90, 'price_old': 22.50,
        'viscosity': '5W-40', 'volume_ml': 1000,
        'is_featured': True, 'is_active': True,
        'short_description_lv': 'Pilnā sintētiskā motoreļļa ar Revitalizants tehnoloģiju',
        'short_description_ru': 'Полностью синтетическое моторное масло с технологией Ревитализант',
        'short_description_en': 'Fully synthetic motor oil with Revitalizant technology',
    },
    {
        'name_lv': 'XADO 5W-30 Synthetic Motor Oil C3 1L',
        'name_ru': 'XADO 5W-30 Синтетическое моторное масло C3 1L',
        'name_en': 'XADO 5W-30 Synthetic Motor Oil C3 1L',
        'name_de': 'XADO 5W-30 Synthetisches Motoröl C3 1L',
        'slug': 'xado-5w30-c3-1l',
        'brand': brands['xado'],
        'category': categories['motor-oils'],
        'price': 19.90,
        'viscosity': '5W-30', 'volume_ml': 1000,
        'is_featured': True, 'is_new': True, 'is_active': True,
        'short_description_lv': 'Sintētiskā motoreļļa moderniem dzinējiem ar daļiņu filtriem',
        'short_description_en': 'Synthetic motor oil for modern engines with DPF',
    },
    {
        'name_lv': 'ATOMEX Multi G 10W-40 Semi-Synthetic 4L',
        'name_ru': 'ATOMEX Multi G 10W-40 Полусинтетика 4L',
        'name_en': 'ATOMEX Multi G 10W-40 Semi-Synthetic 4L',
        'name_de': 'ATOMEX Multi G 10W-40 Halbsynthetisch 4L',
        'slug': 'atomex-10w40-4l',
        'brand': brands['atomex'],
        'category': categories['motor-oils'],
        'price': 32.90, 'price_old': 39.90,
        'viscosity': '10W-40', 'volume_ml': 4000,
        'is_sale': True, 'is_active': True,
        'short_description_lv': 'Pusesintētiskā motoreļļa vispārējai lietošanai',
        'short_description_en': 'Semi-synthetic motor oil for general use',
    },
    {
        'name_lv': 'XADO Revitalizant EX120 dzinējam',
        'name_ru': 'XADO Ревитализант EX120 для двигателя',
        'name_en': 'XADO Revitalizant EX120 for Engine',
        'name_de': 'XADO Revitalizant EX120 für Motor',
        'slug': 'xado-revitalizant-ex120-engine',
        'brand': brands['xado'],
        'category': categories['additives'],
        'price': 24.90,
        'is_featured': True, 'is_active': True,
        'short_description_lv': 'Unikāla piedeva dzinēja atjaunošanai un aizsardzībai',
        'short_description_ru': 'Уникальная присадка для восстановления и защиты двигателя',
        'short_description_en': 'Unique additive for engine restoration and protection',
    },
    {
        'name_lv': 'VERYLUBE Engine Flush Dzinēja skalošana',
        'name_ru': 'VERYLUBE Engine Flush Промывка двигателя',
        'name_en': 'VERYLUBE Engine Flush',
        'name_de': 'VERYLUBE Motor Spülung',
        'slug': 'verylube-engine-flush',
        'brand': brands['verylube'],
        'category': categories['auto-chemistry'],
        'price': 8.50,
        'is_new': True, 'is_active': True,
        'short_description_lv': 'Efektīva dzinēja skalošana pirms eļļas nomaiņas',
        'short_description_en': 'Effective engine flush before oil change',
    },
    {
        'name_lv': 'RED BOOST Dzinēja piedeva 250ml',
        'name_ru': 'RED BOOST Присадка в двигатель 250ml',
        'name_en': 'RED BOOST Engine Additive 250ml',
        'name_de': 'RED BOOST Motoradditiv 250ml',
        'slug': 'red-boost-engine-250ml',
        'brand': brands['red-boost'],
        'category': categories['additives'],
        'price': 14.90,
        'volume_ml': 250,
        'is_featured': True, 'is_active': True,
        'short_description_lv': 'Pastiprina dzinēja jaudu un samazina degvielas patēriņu',
        'short_description_en': 'Boosts engine power and reduces fuel consumption',
    },
]

for p_data in products_data:
    vt = p_data.pop('vehicle_types', None)
    p, created = Product.objects.get_or_create(slug=p_data['slug'], defaults=p_data)
    if not created:
        for k, v in p_data.items():
            setattr(p, k, v)
        p.save()
    print(f"  {p.name_lv[:50]}")

print("\nAuto markas un modeļi...")
car_brands_data = [
    'Toyota', 'Volkswagen', 'BMW', 'Mercedes-Benz', 'Audi',
    'Ford', 'Opel', 'Renault', 'Peugeot', 'Hyundai',
    'Kia', 'Mazda', 'Honda', 'Nissan', 'Volvo',
    'Skoda', 'Seat', 'Fiat', 'Mitsubishi', 'Subaru'
]
car_type = vehicle_types['car']
for brand_name in car_brands_data:
    slug = brand_name.lower().replace(' ', '-').replace('.', '')
    cb, _ = CarBrand.objects.get_or_create(slug=slug, defaults={'name': brand_name})
    cb.vehicle_types.add(car_type)

print("  20 markas pievienotas")

# Toyota modeļi un modifikācijas piemēram
toyota = CarBrand.objects.get(slug='toyota')
vw = CarBrand.objects.get(slug='volkswagen')
bmw = CarBrand.objects.get(slug='bmw')

toyota_models = [
    ('Corolla', [(1.6, 'gasoline', 130, 2019, 2024), (2.0, 'hybrid', 180, 2019, 2024)]),
    ('Camry', [(2.5, 'gasoline', 207, 2018, 2024), (2.5, 'hybrid', 218, 2018, 2024)]),
    ('RAV4', [(2.0, 'gasoline', 175, 2018, 2024), (2.5, 'hybrid', 222, 2019, 2024)]),
    ('Yaris', [(1.0, 'gasoline', 72, 2020, 2024), (1.5, 'hybrid', 116, 2020, 2024)]),
    ('Land Cruiser', [(3.5, 'gasoline', 415, 2021, 2024), (2.8, 'diesel', 204, 2015, 2024)]),
]

for model_name, modifications in toyota_models:
    m, _ = CarModel.objects.get_or_create(brand=toyota, name=model_name, defaults={'vehicle_type': car_type})
    for eng, fuel, hp, y_from, y_to in modifications:
        mod_name = f'{eng}L {fuel.upper()} {hp}hp {y_from}-{y_to}'
        mod, _ = CarModification.objects.get_or_create(
            car_model=m, name=mod_name,
            defaults={'engine_volume': str(eng), 'fuel_type': fuel, 'power_hp': hp, 'year_from': y_from, 'year_to': y_to}
        )

vw_models = [
    ('Golf', [(1.4, 'gasoline', 150, 2012, 2020), (2.0, 'diesel', 150, 2012, 2020), (1.5, 'gasoline', 130, 2020, 2024)]),
    ('Passat', [(2.0, 'diesel', 150, 2015, 2022), (1.8, 'gasoline', 180, 2015, 2022)]),
    ('Tiguan', [(2.0, 'diesel', 150, 2016, 2024), (2.0, 'gasoline', 180, 2016, 2024)]),
    ('Polo', [(1.0, 'gasoline', 95, 2018, 2024), (1.6, 'diesel', 95, 2014, 2020)]),
]
for model_name, modifications in vw_models:
    m, _ = CarModel.objects.get_or_create(brand=vw, name=model_name, defaults={'vehicle_type': car_type})
    for eng, fuel, hp, y_from, y_to in modifications:
        mod_name = f'{eng}L {fuel.upper()} {hp}hp {y_from}-{y_to}'
        mod, _ = CarModification.objects.get_or_create(
            car_model=m, name=mod_name,
            defaults={'engine_volume': str(eng), 'fuel_type': fuel, 'power_hp': hp, 'year_from': y_from, 'year_to': y_to}
        )

print("  Toyota, VW, BMW modeļi pievienoti")

# Pievienojam saderības
xado_5w40 = Product.objects.get(slug='xado-5w40-synthetic-1l')
xado_5w30 = Product.objects.get(slug='xado-5w30-c3-1l')
rev = Product.objects.get(slug='xado-revitalizant-ex120-engine')

for mod in CarModification.objects.filter(car_model__brand__slug__in=['toyota', 'volkswagen'])[:20]:
    if mod.fuel_type in ('gasoline', 'hybrid'):
        ProductCompatibility.objects.get_or_create(product=xado_5w40, modification=mod)
    elif mod.fuel_type == 'diesel':
        ProductCompatibility.objects.get_or_create(product=xado_5w30, modification=mod)
    ProductCompatibility.objects.get_or_create(product=rev, modification=mod)

print("  Saderības pievienotas")

print("\n✓ Demo dati veiksmīgi ievietoti!")
print("Admin: http://127.0.0.1:8000/admin/")
print("Login: admin / admin123")
