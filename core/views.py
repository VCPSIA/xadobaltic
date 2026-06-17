from django.shortcuts import render, get_object_or_404
from catalog.models import Category, Product, Brand, VehicleType
from .models import Banner, NavCategory, Page

SELECTOR_VT_SLUGS = ['passenger-cars', 'light-commercial', 'heavy-truckbus', 'motorcycle', 'agricultural']
NAV_TABS = [
    {'slug': 'passenger-cars', 'vt_slug': 'passenger-cars', 'icon': 'bi-car-front',
     'labels': {'lv': 'Automašīnas',                'ru': 'Легковые авто',       'en': 'Cars',           'de': 'PKW'}},
    {'slug': 'motorcycle',     'vt_slug': 'motorcycle',     'icon': 'bi-bicycle',
     'labels': {'lv': 'Mototehnika',                'ru': 'Мототехника',         'en': 'Motorcycles',    'de': 'Motorräder'}},
    {'slug': 'heavy-truckbus', 'vt_slug': 'heavy-truckbus', 'icon': 'bi-truck',
     'labels': {'lv': 'Kravas auto un cita tehnika','ru': 'Грузовой транспорт',  'en': 'Trucks & more',  'de': 'LKW & Technik'}},
    {'slug': 'ieroci',         'vt_slug': None,             'icon': 'bi-crosshair',
     'labels': {'lv': 'Ieroči',                     'ru': 'Оружие',              'en': 'Weapons',        'de': 'Waffen'}},
]


def index(request):
    banners = Banner.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    if not featured_products:
        featured_products = Product.objects.filter(is_active=True).select_related('brand')[:8]
    new_products = Product.objects.filter(is_active=True, is_new=True)[:8]
    if not new_products:
        new_products = Product.objects.filter(is_active=True).select_related('brand')[8:16]
    sale_products = Product.objects.filter(is_active=True, is_sale=True)[:8]
    top_categories = Category.objects.filter(is_active=True, parent=None)[:8]
    brands = Brand.objects.filter(is_active=True)
    vt_qs = VehicleType.objects.filter(slug__in=SELECTOR_VT_SLUGS)
    slug_order = {s: i for i, s in enumerate(SELECTOR_VT_SLUGS)}
    vehicle_types = sorted(vt_qs, key=lambda vt: slug_order.get(vt.slug, 99))

    lang = request.LANGUAGE_CODE[:2] if hasattr(request, 'LANGUAGE_CODE') else 'lv'
    all_tab_slugs = [t['slug'] for t in NAV_TABS]
    vt_slugs = [t['vt_slug'] for t in NAV_TABS if t['vt_slug']]
    vt_by_slug = {vt.slug: vt for vt in VehicleType.objects.filter(slug__in=vt_slugs)}

    from django.db.models import Prefetch
    nav_cats_by_slug = {}
    top_cats = NavCategory.objects.filter(
        tab_slug__in=all_tab_slugs, is_active=True, parent__isnull=True
    ).prefetch_related(
        Prefetch('children', queryset=NavCategory.objects.filter(is_active=True).order_by('order', 'name_lv'))
    )
    for nc in top_cats:
        nav_cats_by_slug.setdefault(nc.tab_slug, []).append(nc)

    nav_vts = []
    for tab in NAV_TABS:
        slug = tab['slug']
        vt = vt_by_slug.get(tab['vt_slug']) if tab['vt_slug'] else None
        nav_vts.append({
            'id':           vt.id if vt else None,
            'slug':         slug,
            'icon':         tab['icon'],
            'name':         tab['labels'].get(lang) or tab['labels']['lv'],
            'subcats':      nav_cats_by_slug.get(slug, []),
            'has_selector': vt is not None,
        })

    return render(request, 'index.html', {
        'banners': banners,
        'featured_products': featured_products,
        'new_products': new_products,
        'sale_products': sale_products,
        'top_categories': top_categories,
        'brands': brands,
        'vehicle_types': vehicle_types,
        'nav_vts': nav_vts,
    })


def nav_category_detail(request, pk):
    cat = get_object_or_404(NavCategory, pk=pk, parent__isnull=True, is_active=True)
    subcats = cat.children.filter(is_active=True).order_by('order', 'name_lv')
    lang = request.LANGUAGE_CODE[:2]
    cat_name = getattr(cat, f'name_{lang}', '') or cat.name_lv
    tab_label = next(
        (t['labels'].get(lang) or t['labels']['lv'] for t in NAV_TABS if t['slug'] == cat.tab_slug),
        cat.tab_slug
    )
    return render(request, 'core/nav_category.html', {
        'cat': cat,
        'cat_name': cat_name,
        'tab_label': tab_label,
        'subcats': subcats,
        'lang': lang,
    })


TAB_BOOL_MAP = {
    'passenger-cars':  'tab_passenger_cars',
    'heavy-truckbus':  'tab_heavy_truckbus',
    'motorcycle':      'tab_motorcycle',
    'ieroci':          'tab_ieroci',
}


def nav_subcategory_products(request, pk):
    from catalog.models import Product
    subcat = get_object_or_404(NavCategory, pk=pk, parent__isnull=False, is_active=True)
    lang = request.LANGUAGE_CODE[:2]
    subcat_name = getattr(subcat, f'name_{lang}', '') or subcat.name_lv
    parent_name = getattr(subcat.parent, f'name_{lang}', '') or subcat.parent.name_lv
    tab_label = next(
        (t['labels'].get(lang) or t['labels']['lv'] for t in NAV_TABS if t['slug'] == subcat.tab_slug),
        subcat.tab_slug
    )

    # Atrast ekvivalentās apakškategorijas (vienāds nosaukums un virskategorija visiem tabiem)
    equiv_pks = NavCategory.objects.filter(
        parent__isnull=False,
        name_lv=subcat.name_lv,
        parent__name_lv=subcat.parent.name_lv,
    ).values_list('pk', flat=True)

    # Filtrēt produktus pēc apakškategorijas UN taba boolean lauka
    tab_field = TAB_BOOL_MAP.get(subcat.tab_slug)
    if tab_field:
        products = Product.objects.filter(
            is_active=True,
            nav_subcategory__in=equiv_pks,
            **{tab_field: True},
        ).select_related('brand').order_by('order', 'name_lv')
    else:
        products = Product.objects.filter(
            is_active=True,
            nav_subcategory__in=equiv_pks,
        ).select_related('brand').order_by('order', 'name_lv')

    return render(request, 'core/nav_subcategory.html', {
        'subcat': subcat,
        'subcat_name': subcat_name,
        'parent_name': parent_name,
        'tab_label': tab_label,
        'products': products,
        'lang': lang,
    })


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    lang = request.LANGUAGE_CODE[:2]
    title = getattr(page, f'title_{lang}', '') or page.title_lv
    content = getattr(page, f'content_{lang}', '') or page.content_lv
    return render(request, 'core/page_detail.html', {
        'page': page,
        'title': title,
        'content': content,
    })


def contact(request):
    return render(request, 'core/contact.html')
