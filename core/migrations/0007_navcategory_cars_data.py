from django.db import migrations


CARS_SUBCATEGORIES = [
    ('Dzesēšanas sistēma',     'bi-thermometer-half',      0),
    ('Dzinējs',                'bi-gear-wide-connected',   1),
    ('Degvielas sistēma',      'bi-droplet-fill',          2),
    ('Kondicionēšanas sistēma','bi-wind',                  3),
    ('Virsbūve un salons',     'bi-car-front',             4),
    ('Transmisija',            'bi-gear',                  5),
    ('Stūres sistēma',         'bi-arrow-left-right',      6),
    ('Riepas',                 'bi-circle',                7),
    ('Citi mezgli un mehānismi','bi-tools',                8),
]


def add_cars_subcategories(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    VehicleType = apps.get_model('catalog', 'VehicleType')
    try:
        vt = VehicleType.objects.get(slug='passenger-cars')
    except VehicleType.DoesNotExist:
        return
    for name, icon, order in CARS_SUBCATEGORIES:
        NavCategory.objects.get_or_create(
            vehicle_type=vt,
            name_lv=name,
            defaults={'icon': icon, 'order': order, 'is_active': True},
        )


def remove_cars_subcategories(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    VehicleType = apps.get_model('catalog', 'VehicleType')
    try:
        vt = VehicleType.objects.get(slug='passenger-cars')
        NavCategory.objects.filter(vehicle_type=vt).delete()
    except VehicleType.DoesNotExist:
        pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_navcategory'),
        ('catalog', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(add_cars_subcategories, remove_cars_subcategories),
    ]
