from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0019_kravas_auto_subcats')]

    operations = [
        migrations.AddField(
            model_name='navcategory',
            name='image',
            field=models.ImageField(
                blank=True,
                upload_to='nav_categories/',
                help_text='Mazs attēls nolaižamajā kategoriju sarakstā',
            ),
        ),
    ]
