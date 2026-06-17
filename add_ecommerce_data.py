import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadobaltic.settings')
django.setup()

from catalog.models import Product, ProductVolume, ProductSpecification, ProductApplication

print("Pielietojumi...")
apps_data = [
    ('Dzinējs', 'Двигатель', 'Engine', 'Motor', 'engine', 'bi-gear'),
    ('Transmisija', 'Трансмиссия', 'Transmission', 'Getriebe', 'transmission', 'bi-arrows-angle-expand'),
    ('Degvielas sistēma', 'Топливная система', 'Fuel system', 'Kraftstoffsystem', 'fuel-system', 'bi-droplet-half'),
    ('Dzesēšanas sistēma', 'Система охлаждения', 'Cooling system', 'Kühlsystem', 'cooling', 'bi-thermometer'),
    ('Stūres pastiprinātājs', 'Гидроусилитель руля', 'Power steering', 'Servolenkung', 'power-steering', 'bi-arrow-left-right'),
    ('Bremžu sistēma', 'Тормозная система', 'Brake system', 'Bremssystem', 'brakes', 'bi-octagon'),
    ('Eļļas sistēma', 'Масляная система', 'Oil system', 'Ölsystem', 'oil-system', 'bi-droplet-fill'),
    ('Automašīnas ārpuse', 'Кузов автомобиля', 'Car body', 'Fahrzeugkarosserie', 'car-body', 'bi-car-front'),
]
apps = {}
for lv, ru, en, de, slug, icon in apps_data:
    app, _ = ProductApplication.objects.get_or_create(slug=slug, defaults={
        'name_lv': lv, 'name_ru': ru, 'name_en': en, 'name_de': de, 'icon': icon
    })
    apps[slug] = app
    print(f"  {lv}")

print("\nTilpumi produktiem...")
volumes_data = {
    'xado-5w40-synthetic-1l': [
        ('1L', 1000, 'XB-5W40-1L', 18.90, 22.50, True),
        ('4L', 4000, 'XB-5W40-4L', 62.90, None, False),
        ('5L', 5000, 'XB-5W40-5L', 74.90, None, False),
    ],
    'xado-5w30-c3-1l': [
        ('1L', 1000, 'XB-5W30-1L', 19.90, None, True),
        ('4L', 4000, 'XB-5W30-4L', 69.90, None, False),
        ('5L', 5000, 'XB-5W30-5L', 84.90, None, False),
    ],
    'atomex-10w40-4l': [
        ('1L', 1000, 'AT-10W40-1L', 9.90, 12.50, False),
        ('4L', 4000, 'AT-10W40-4L', 32.90, 39.90, True),
        ('5L', 5000, 'AT-10W40-5L', 39.90, 49.90, False),
    ],
    'xado-revitalizant-ex120-engine': [
        ('9ml', 9, 'XR-EX120-9', 24.90, None, True),
        ('25ml', 25, 'XR-EX120-25', 54.90, None, False),
    ],
    'verylube-engine-flush': [
        ('250ml', 250, 'VL-EF-250', 8.50, None, True),
        ('400ml', 400, 'VL-EF-400', 11.90, None, False),
    ],
    'red-boost-engine-250ml': [
        ('250ml', 250, 'RB-EN-250', 14.90, None, True),
        ('500ml', 500, 'RB-EN-500', 24.90, 28.90, False),
    ],
}

for slug, vols in volumes_data.items():
    try:
        product = Product.objects.get(slug=slug)
        for label, ml, sku, price, price_old, is_default in vols:
            pv, created = ProductVolume.objects.get_or_create(
                product=product, label=label,
                defaults={
                    'volume_ml': ml, 'sku': sku,
                    'price': price, 'price_old': price_old,
                    'is_default': is_default, 'is_active': True
                }
            )
        print(f"  {product.name_lv}: {len(vols)} tilpumi")
    except Product.DoesNotExist:
        print(f"  Prece nav atrasta: {slug}")

print("\nSpecifikācijas...")
specs_data = {
    'xado-5w40-synthetic-1l': [
        ('API standarts', 'API Standard', 'API Norm', 'API-Норма', 'SN/CF'),
        ('ACEA klase', 'ACEA Class', 'ACEA Klasse', 'ACEA класс', 'A3/B4'),
        ('Viskozitāte', 'Viscosity', 'Viskosität', 'Вязкость', '5W-40'),
        ('Bāze', 'Base', 'Basis', 'Основа', 'Pilnā sintētika'),
        ('Tilpums', 'Volume', 'Volumen', 'Объём', '1L, 4L, 5L'),
    ],
    'xado-5w30-c3-1l': [
        ('API standarts', 'API Standard', 'API Norm', 'API-Норма', 'SN/CF'),
        ('ACEA klase', 'ACEA Class', 'ACEA Klasse', 'ACEA класс', 'C3'),
        ('Viskozitāte', 'Viscosity', 'Viskosität', 'Вязкость', '5W-30'),
        ('Bāze', 'Base', 'Basis', 'Основа', 'Pilnā sintētika'),
        ('Atbilstība', 'Compliance', 'Einhaltung', 'Соответствие', 'BMW LL-04, VW 507.00, MB 229.31'),
    ],
    'atomex-10w40-4l': [
        ('API standarts', 'API Standard', 'API Norm', 'API-Норма', 'SL/CF'),
        ('ACEA klase', 'ACEA Class', 'ACEA Klasse', 'ACEA класс', 'A3/B3'),
        ('Viskozitāte', 'Viscosity', 'Viskosität', 'Вязкость', '10W-40'),
        ('Bāze', 'Base', 'Basis', 'Основа', 'Pusesintētika'),
    ],
    'xado-revitalizant-ex120-engine': [
        ('Tips', 'Type', 'Typ', 'Тип', 'Revitalizants'),
        ('Pielietojums', 'Application', 'Anwendung', 'Применение', 'Visi benzīna un dīzeļdzinēji'),
        ('Efekts', 'Effect', 'Wirkung', 'Эффект', 'Dzinēja atjaunošana un aizsardzība'),
        ('Deva', 'Dose', 'Dosis', 'Доза', '1 flakons uz 4-5L eļļas'),
    ],
}

for slug, specs in specs_data.items():
    try:
        product = Product.objects.get(slug=slug)
        for i, (lv, en, de, ru, value) in enumerate(specs):
            ProductSpecification.objects.get_or_create(
                product=product, name_lv=lv,
                defaults={'name_en': en, 'name_de': de, 'name_ru': ru, 'value': value, 'order': i}
            )
        print(f"  {product.name_lv}: {len(specs)} spec.")
    except Product.DoesNotExist:
        pass

print("\nPielietojumu saistīšana ar produktiem...")
engine_app = apps['engine']
for slug in ['xado-5w40-synthetic-1l', 'xado-5w30-c3-1l', 'atomex-10w40-4l', 'xado-revitalizant-ex120-engine', 'red-boost-engine-250ml']:
    try:
        p = Product.objects.get(slug=slug)
        p.applications.add(engine_app)
        p.applications.add(apps['oil-system'])
    except Product.DoesNotExist:
        pass

try:
    flush = Product.objects.get(slug='verylube-engine-flush')
    flush.applications.add(engine_app)
    flush.applications.add(apps['oil-system'])
except Product.DoesNotExist:
    pass

print("  Saistītas!")
print("\nGatavs! Demo dati pievienoti.")
