from django.shortcuts import render
from django.http import JsonResponse
from .models import CarBrand, CarModel, CarModification, ProductCompatibility
from catalog.models import Product

LM_CATS = {
    1: {'name_lv': 'Automašīnas', 'name_ru': 'ŠŠ²Ń‚Š¾Š¼Š¾Š±ŠøŠ»Šø', 'name_en': 'Cars', 'name_de': 'Pkw', 'icon': 'bi-car-front-fill'},
    2: {'name_lv': 'Furgoni un pikapi', 'name_ru': 'Š¤ŃŃ€Š³Š¾Š½Ń‹ Šø ŠæŠøŠŗŠ°ŠæŃ‹', 'name_en': 'Vans & Pickups', 'name_de': 'Transporter', 'icon': 'bi-truck'},
    3: {'name_lv': 'Kravas auto un autobusi', 'name_ru': 'Š“Ń€ŃŠ·Š¾Š²ŠøŠŗŠø Šø Š°Š²Ń‚Š¾Š±ŃŃŃ‹', 'name_en': 'Trucks & Buses', 'name_de': 'LKW', 'icon': 'bi-bus-front-fill'},
    4: {'name_lv': 'Motocikli', 'name_ru': 'ŠŠ¾Ń‚Š¾Ń†ŠøŠŗŠ»Ń‹', 'name_en': 'Motorcycles', 'name_de': 'MotorrĆ¤der', 'icon': 'bi-bicycle'},
}


def selector(request):
    lang = getattr(request, 'LANGUAGE_CODE', 'lv')[:2]
    categories = []
    for cat_id, info in LM_CATS.items():
        name = info.get(f'name_{lang}') or info['name_lv']
        categories.append({'id': cat_id, 'name': name, 'icon': info['icon']})
    return render(request, 'selector/selector.html', {'lm_categories': categories})


def api_brands(request):
    lm_cat = request.GET.get('lm_cat')
    show_all = request.GET.get('all') == '1'

    brands = CarBrand.objects.filter(is_active=True, lm_id__gt='')
    if lm_cat:
        brands = brands.filter(models__lm_category=lm_cat).distinct()

    # Parādam tikai EU + neregionālās markas (bez USA/MENA/CHN/TUR/THA/BRA/RUS/AUS)
    if not show_all:
        from django.db.models import Q
        brands = brands.filter(
            Q(name__endswith=' (EU)') |
            ~Q(name__regex=r'\((?:EU|USA|MENA|CHN|TUR|THA|BRA|RUS|AUS|USA / CAN|USA/CAN|IND)\)')
        )

    brands = brands.order_by('name')

    data = []
    for b in brands:
        # Noņemam "(EU)" sufiksu no displeja nosaukuma
        display = b.name.replace(' (EU)', '').strip()
        data.append({'id': b.id, 'name': display})
    return JsonResponse(data, safe=False)


def api_models(request):
    brand_id = request.GET.get('brand')
    lm_cat = request.GET.get('lm_cat')
    if not brand_id:
        return JsonResponse([], safe=False)
    models = CarModel.objects.filter(brand_id=brand_id, is_active=True, lm_id__gt='')
    if lm_cat:
        models = models.filter(lm_category=lm_cat)
    models = models.order_by('name')
    data = [{'id': m.id, 'name': m.name, 'year_from': m.year_from, 'year_to': m.year_to} for m in models]
    return JsonResponse(data, safe=False)


def api_modifications(request):
    model_id = request.GET.get('model')
    if not model_id:
        return JsonResponse([], safe=False)
    mods = CarModification.objects.filter(
        car_model_id=model_id, is_active=True, lm_id__gt=''
    ).order_by('name')
    data = [{'id': m.id, 'name': m.name, 'year_from': m.year_from, 'year_to': m.year_to,
             'has_visc': bool(m.oil_viscosity)} for m in mods]
    return JsonResponse(data, safe=False)


def _products_by_viscosity(viscosity, oil_spec, lang):
    oem_tokens = [t.strip().lower() for t in oil_spec.split(',') if t.strip()] if oil_spec else []
    visc_list = [v.strip() for v in viscosity.split(',') if v.strip()]
    if not visc_list:
        return []
    prods = Product.objects.filter(
        is_active=True, viscosity__in=visc_list
    ).select_related('brand', 'category').order_by('order', 'name_lv')
    scored = []
    for p in prods:
        score = _score_product(p, oem_tokens) if oem_tokens else 0
        scored.append((score, p))
    scored.sort(key=lambda x: -x[0])
    result = []
    for score, p in scored:
        name = getattr(p, f'name_{lang}', '') or p.name_lv
        short_desc = getattr(p, f'short_description_{lang}', '') or p.short_description_lv
        result.append({
            'id': p.id, 'name': name, 'slug': p.slug,
            'brand': p.brand.name if p.brand else '',
            'price': str(p.price) if p.price else '',
            'price_old': str(p.price_old) if p.price_old else '',
            'image': p.main_image.url if p.main_image else '',
            'viscosity': p.viscosity,
            'short_description': short_desc,
            'note': '',
            'match': 'spec' if score > 0 else 'viscosity',
            'score': score,
        })
    return result


def _score_product(prod, oem_tokens):
    """Skaitām cik OEM tokeni atbilst produkta specifikācijām. Augstāks = labāks."""
    combined = ' '.join([
        prod.specifications_lv or '',
        prod.requirements_lv or '',
    ]).lower()
    score = 0
    for token in oem_tokens:
        if token in combined:
            score += 1
    return score


def api_products(request):
    modification_id = request.GET.get('modification')
    if not modification_id:
        return JsonResponse({'products': [], 'viscosity': '', 'oil_spec': ''})

    lang = getattr(request, 'LANGUAGE_CODE', 'lv')[:2]

    try:
        mod = CarModification.objects.get(pk=modification_id)
    except CarModification.DoesNotExist:
        return JsonResponse({'products': [], 'viscosity': '', 'oil_spec': ''})

    viscosity = mod.oil_viscosity
    oil_spec = mod.oil_spec
    products = []

    oem_tokens = []
    if oil_spec:
        oem_tokens = [t.strip().lower() for t in oil_spec.split(',') if t.strip()]

    # Primārais avots: ProductCompatibility ieraksti šai modifikācijai
    compat_qs = ProductCompatibility.objects.filter(
        modification_id=modification_id, product__is_active=True
    ).select_related('product', 'product__brand', 'product__category')

    if compat_qs.exists():
        scored = []
        for c in compat_qs:
            p = c.product
            score = _score_product(p, oem_tokens) if oem_tokens else 0
            scored.append((score, p, getattr(c, f'note_{lang}', '') or c.note_lv))
        scored.sort(key=lambda x: -x[0])
        for score, p, note in scored:
            name = getattr(p, f'name_{lang}', '') or p.name_lv
            short_desc = getattr(p, f'short_description_{lang}', '') or p.short_description_lv
            products.append({
                'id': p.id, 'name': name, 'slug': p.slug,
                'brand': p.brand.name if p.brand else '',
                'price': str(p.price) if p.price else '',
                'price_old': str(p.price_old) if p.price_old else '',
                'image': p.main_image.url if p.main_image else '',
                'viscosity': p.viscosity,
                'short_description': short_desc,
                'note': note,
                'match': 'spec' if score > 0 else 'compat',
                'score': score,
            })
    elif viscosity:
        # Rezerves variants: filtrē pēc viskozitātes, ja nav compat ierakstu
        products = _products_by_viscosity(viscosity, oil_spec, lang)

    if not products:
        # Meklē compat ierakstus citās tā paša modeļa modifikācijās
        sibling_compat = ProductCompatibility.objects.filter(
            modification__car_model=mod.car_model,
            product__is_active=True
        ).exclude(modification=mod).select_related('product', 'product__brand', 'product__category')
        if sibling_compat.exists():
            seen_ids = set()
            scored = []
            for c in sibling_compat:
                p = c.product
                if p.id in seen_ids:
                    continue
                seen_ids.add(p.id)
                score = _score_product(p, oem_tokens) if oem_tokens else 0
                scored.append((score, p))
            scored.sort(key=lambda x: -x[0])
            for score, p in scored:
                name = getattr(p, f'name_{lang}', '') or p.name_lv
                short_desc = getattr(p, f'short_description_{lang}', '') or p.short_description_lv
                products.append({
                    'id': p.id, 'name': name, 'slug': p.slug,
                    'brand': p.brand.name if p.brand else '',
                    'price': str(p.price) if p.price else '',
                    'price_old': str(p.price_old) if p.price_old else '',
                    'image': p.main_image.url if p.main_image else '',
                    'viscosity': p.viscosity,
                    'short_description': short_desc,
                    'note': '',
                    'match': 'spec' if score > 0 else 'model',
                    'score': score,
                })

    if not products:
        # Izmanto tā paša modeļa citu modifikāciju viskozitāti
        sibling_viscs = CarModification.objects.filter(
            car_model=mod.car_model
        ).exclude(oil_viscosity='').values_list('oil_viscosity', flat=True)
        if sibling_viscs.exists():
            all_visc = set()
            for sv in sibling_viscs:
                for v in sv.split(','):
                    all_visc.add(v.strip())
            sibling_oil_spec = CarModification.objects.filter(
                car_model=mod.car_model
            ).exclude(oil_spec='').values_list('oil_spec', flat=True).first() or ''
            products = _products_by_viscosity(','.join(all_visc), sibling_oil_spec, lang)

    return JsonResponse({'products': products, 'viscosity': viscosity, 'oil_spec': oil_spec})

