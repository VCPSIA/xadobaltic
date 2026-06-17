from django.db import migrations

CATS = [
    ('2-taktu motoreļļa', 'bi-droplet-fill',       0),
    ('4-taktu motoreļļa', 'bi-droplet-half',        1),
    ('Revitalizanti',     'bi-tools',               2),
    ('Smērvielas',        'bi-droplet',             3),
]


def add_cats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    for name, icon, order in CATS:
        NavCategory.objects.get_or_create(
            name_lv=name, tab_slug='motorcycle', parent=None,
            defaults={'icon': icon, 'order': order, 'is_active': True},
        )


def remove_cats(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    NavCategory.objects.filter(
        tab_slug='motorcycle', parent__isnull=True,
        name_lv__in=[c[0] for c in CATS],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [('core', '0024_sitesettings_viber')]
    operations = [migrations.RunPython(add_cats, remove_cats)]
