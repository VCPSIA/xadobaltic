from django.db import migrations


def populate_tab_slugs(apps, schema_editor):
    NavCategory = apps.get_model('core', 'NavCategory')
    for nc in NavCategory.objects.filter(vehicle_type__isnull=False, tab_slug=''):
        nc.tab_slug = nc.vehicle_type.slug
        nc.save()


class Migration(migrations.Migration):
    dependencies = [('core', '0008_navcategory_tab_slug')]
    operations = [migrations.RunPython(populate_tab_slugs, migrations.RunPython.noop)]
