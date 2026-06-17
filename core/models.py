from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address_lv = models.TextField(blank=True)
    address_ru = models.TextField(blank=True)
    address_en = models.TextField(blank=True)
    address_de = models.TextField(blank=True)
    whatsapp = models.CharField(max_length=30, blank=True,
                               help_text='Starptautiskais formāts bez + un atstarpēm, piemēram: 37126123456')
    viber = models.CharField(max_length=30, blank=True,
                             help_text='Starptautiskais formāts bez + un atstarpēm, piemēram: 37126123456')
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Vietnes iestatījumi'
        verbose_name_plural = 'Vietnes iestatījumi'

    def __str__(self):
        return 'Vietnes iestatījumi'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


TEXT_ALIGN_CHOICES = [
    ('left', 'Pa kreisi'),
    ('center', 'Centrā'),
    ('right', 'Pa labi'),
]
TEXT_VALIGN_CHOICES = [
    ('top', 'Augšā'),
    ('middle', 'Vidū'),
    ('bottom', 'Apakšā'),
]
TRANSITION_CHOICES = [
    ('slide',    'Slīdēšana (noklusējums)'),
    ('fade',     'Izbalēšana'),
    ('zoom-in',  'Palielināšanās (no maza uz lielu)'),
    ('zoom-out', 'Samazināšanās (no liela uz mazu)'),
    ('mosaic',   'Mozaīkas kvadrātiņi'),
]
FONT_FAMILY_CHOICES = [
    ('Inter, sans-serif', 'Inter (noklusējums)'),
    ('Arial, sans-serif', 'Arial'),
    ('Georgia, serif', 'Georgia'),
    ("'Oswald', sans-serif", 'Oswald'),
    ("'Roboto', sans-serif", 'Roboto'),
]


class Banner(models.Model):
    title_lv = models.CharField(max_length=200, blank=True)
    title_ru = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)
    title_de = models.CharField(max_length=200, blank=True)
    subtitle_lv = models.TextField(blank=True)
    subtitle_ru = models.TextField(blank=True)
    subtitle_en = models.TextField(blank=True)
    subtitle_de = models.TextField(blank=True)
    button_text_lv = models.CharField(max_length=100, blank=True)
    button_text_ru = models.CharField(max_length=100, blank=True)
    button_text_en = models.CharField(max_length=100, blank=True)
    button_text_de = models.CharField(max_length=100, blank=True)
    button_url = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='banners/', blank=True)
    image_mobile = models.ImageField(upload_to='banners/', blank=True)
    image_opacity = models.FloatField(default=1.0, help_text='0.1 = gandrīz caurspīdīgs, 1.0 = necaurspīdīgs')
    text_align = models.CharField(max_length=10, choices=TEXT_ALIGN_CHOICES, default='left')
    text_valign = models.CharField(max_length=10, choices=TEXT_VALIGN_CHOICES, default='bottom')
    font_size = models.PositiveIntegerField(default=48, help_text='Virsraksta burtu lielums pikseļos')
    font_family = models.CharField(max_length=100, choices=FONT_FAMILY_CHOICES, default='Inter, sans-serif')
    transition_effect = models.CharField(max_length=20, choices=TRANSITION_CHOICES, default='slide')
    slide_duration = models.PositiveIntegerField(default=5000, help_text='Rādīšanas ilgums milisekundēs (5000 = 5 sek)')
    title_color = models.CharField(max_length=7, default='#ffffff', help_text='Virsraksta krāsa (hex)')
    subtitle_color = models.CharField(max_length=7, default='#cccccc', help_text='Apakšvirsraksta krāsa (hex)')
    button_bg_color = models.CharField(max_length=7, default='#e30613', help_text='Pogas fona krāsa (hex)')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Baneris'
        verbose_name_plural = 'Baneri'
        ordering = ['order']

    def __str__(self):
        return self.title_lv or self.title_en or f'Baneris #{self.pk}'


class NavCategory(models.Model):
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='children',
        verbose_name='Vecākkategorija',
    )
    TAB_CHOICES = [
        ('passenger-cars',  'Automašīnas'),
        ('motorcycle',      'Mototehnika'),
        ('heavy-truckbus',  'Kravas auto un cita tehnika'),
        ('ieroci',          'Ieroči'),
    ]
    tab_slug = models.SlugField(max_length=50, default='', choices=TAB_CHOICES,
                                verbose_name='Tab')
    vehicle_type = models.ForeignKey(
        'catalog.VehicleType',
        on_delete=models.SET_NULL,
        related_name='nav_categories',
        verbose_name='Transportlīdzekļa tips',
        null=True, blank=True,
    )
    name_lv = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100, blank=True)
    name_en = models.CharField(max_length=100, blank=True)
    name_de = models.CharField(max_length=100, blank=True)
    icon = models.CharField(max_length=100, blank=True, default='bi-circle',
                            help_text='Bootstrap Icon klase, piemēram: bi-gear')
    image = models.ImageField(upload_to='nav_categories/', blank=True,
                              help_text='Mazs attēls nolaižamajā kategoriju sarakstā')
    url = models.CharField(max_length=500, blank=True,
                           help_text='Saite uz kuru ved klikšķinot')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Navigācijas apakškategorija'
        verbose_name_plural = 'Navigācijas apakškategorijas'
        ordering = ['name_lv']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name_lv} › {self.name_lv}'
        return f'{self.tab_slug} › {self.name_lv}'


class Page(models.Model):
    slug = models.SlugField(unique=True)
    title_lv = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)
    title_de = models.CharField(max_length=200, blank=True)
    content_lv = models.TextField()
    content_ru = models.TextField(blank=True)
    content_en = models.TextField(blank=True)
    content_de = models.TextField(blank=True)
    meta_description_lv = models.TextField(blank=True)
    meta_description_ru = models.TextField(blank=True)
    meta_description_en = models.TextField(blank=True)
    meta_description_de = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lapa'
        verbose_name_plural = 'Lapas'

    def __str__(self):
        return self.title_lv or self.slug
