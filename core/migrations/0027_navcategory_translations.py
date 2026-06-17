from django.db import migrations

# name_lv: (name_de, name_en, name_ru)
TRANSLATIONS = {
    # Augšlīmeņa kategorijas
    'Bremžu sistēma':              ('Bremssystem',               'Brake System',              'Тормозная система'),
    'Citi mezgli un mehānismi':    ('Andere Baugruppen',          'Other Components',          'Другие узлы и механизмы'),
    'Degvielas sistēma':           ('Kraftstoffsystem',           'Fuel System',               'Топливная система'),
    'Dzesēšanas sistēma':          ('Kühlsystem',                 'Cooling System',            'Система охлаждения'),
    'Dzinējs':                     ('Motor',                      'Engine',                    'Двигатель'),
    'Riepas':                      ('Reifen',                     'Tyres',                     'Шины'),
    'Stūres sistēma':              ('Lenksystem',                 'Steering System',           'Рулевая система'),
    'Transmisija':                 ('Getriebe',                   'Transmission',              'Трансмиссия'),
    'Virsbūve un salons':          ('Karosserie und Innenraum',   'Body and Interior',         'Кузов и салон'),
    # Mototehnika
    '2-taktu motoreļļa':           ('2-Takt-Motoröl',             '2-Stroke Engine Oil',       'Моторное масло 2-тактное'),
    '4-taktu motoreļļa':           ('4-Takt-Motoröl',             '4-Stroke Engine Oil',       'Моторное масло 4-тактное'),
    'Smērvielas':                  ('Schmiermittel',              'Lubricants',                'Смазочные материалы'),
    # Ieroči
    'Ieroču kopšanas līdzekļi':    ('Waffenpflegemittel',         'Weapon Care Products',      'Средства для ухода за оружием'),
    'Revitalizants':               ('Revitalisator',              'Revitalizant',              'Ревитализант'),
    # Apakškategorijas
    'Antifrīzs':                   ('Frostschutzmittel',          'Antifreeze',                'Антифриз'),
    'Attīrītāji':                  ('Reiniger',                   'Cleaners',                  'Очистители'),
    'Līdzekļi radiatoram':         ('Kühlmittel',                 'Radiator Products',         'Средства для радиатора'),
    'Eļļas':                       ('Öle',                        'Oils',                      'Масла'),
    'Eļļa':                        ('Öl',                         'Oil',                       'Масло'),
    'Metāla kondicionieri':        ('Metallkonditionierer',       'Metal Conditioners',        'Кондиционеры металла'),
    'Revitalizanti':               ('Revitalisatoren',            'Revitalizants',             'Ревитализанты'),
    'Citi līdzekļi':               ('Andere Mittel',              'Other Products',            'Другие средства'),
    'Degvielas piedevas':          ('Kraftstoffzusätze',          'Fuel Additives',            'Топливные присадки'),
    'Apkopes līdzekļi':            ('Wartungsmittel',             'Maintenance Products',      'Средства обслуживания'),
    'Biezās smērvielas':           ('Schmierfette',               'Greases',                   'Густые смазки'),
    'Iekļūstošās smērvielas':      ('Kriechöle',                  'Penetrating Lubricants',    'Проникающие смазки'),
    'Līdzekļi salona kopšanai':    ('Innenraumpflegemittel',      'Interior Care Products',    'Средства для ухода за салоном'),
    'Līdzekļi virsbūves un stiklu kopšanai': (
                                    'Karosserie- und Glasreiniger','Body and Glass Care',      'Средства для кузова и стекол'),
}


def add_translations(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    for name_lv, (de, en, ru) in TRANSLATIONS.items():
        NavCategory.objects.filter(name_lv=name_lv).update(
            name_de=de, name_en=en, name_ru=ru,
        )


def remove_translations(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    NavCategory.objects.all().update(name_de='', name_en='', name_ru='')


class Migration(migrations.Migration):
    dependencies = [('core', '0026_ieroci_cats')]
    operations = [migrations.RunPython(add_translations, remove_translations)]
