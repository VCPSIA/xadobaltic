from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Category, Product, Brand, Review, WishlistItem

COMPARE_SESSION_KEY = 'xado_compare'
WISHLIST_SESSION_KEY = 'xado_wishlist'


def category_list(request):
    categories = Category.objects.filter(is_active=True, parent=None).prefetch_related('children')
    all_products = Product.objects.filter(is_active=True).select_related('brand').prefetch_related('volumes')
    brand_filter = request.GET.get('brand')
    if brand_filter:
        all_products = all_products.filter(brand__slug=brand_filter)
    q = request.GET.get('q', '').strip()
    if q:
        all_products = all_products.filter(name_lv__icontains=q) | \
                       all_products.filter(name_ru__icontains=q) | \
                       all_products.filter(name_en__icontains=q)
    brands = Brand.objects.filter(is_active=True, products__is_active=True).distinct()
    return render(request, 'catalog/category_list.html', {
        'categories': categories,
        'all_products': all_products,
        'brands': brands,
        'selected_brand': brand_filter,
        'q': q,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    subcategories = category.children.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    if subcategories.exists():
        cat_ids = list(subcategories.values_list('pk', flat=True)) + [category.pk]
        products = products.filter(category_id__in=cat_ids)
    else:
        products = products.filter(category=category)
    brand_filter = request.GET.get('brand')
    if brand_filter:
        products = products.filter(brand__slug=brand_filter)
    brands = Brand.objects.filter(products__in=products).distinct()
    return render(request, 'catalog/category_detail.html', {
        'category': category,
        'subcategories': subcategories,
        'products': products,
        'brands': brands,
        'selected_brand': brand_filter,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.filter(is_approved=True)
    avg_rating = None
    if reviews.exists():
        avg_rating = round(sum(r.rating for r in reviews) / reviews.count(), 1)

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=product).exists()
    else:
        wl = request.session.get(WISHLIST_SESSION_KEY, [])
        in_wishlist = product.pk in wl

    compare_ids = request.session.get(COMPARE_SESSION_KEY, [])
    in_compare = product.pk in compare_ids

    related = Product.objects.filter(is_active=True, brand=product.brand).exclude(pk=product.pk)[:4]
    if not related:
        related = Product.objects.filter(is_active=True).exclude(pk=product.pk)[:4]

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
        'in_wishlist': in_wishlist,
        'in_compare': in_compare,
        'compare_count': len(compare_ids),
    })


def brand_list(request):
    brands = Brand.objects.filter(is_active=True)
    return render(request, 'catalog/brand_list.html', {'brands': brands})


def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products = Product.objects.filter(brand=brand, is_active=True)
    return render(request, 'catalog/brand_detail.html', {
        'brand': brand,
        'products': products,
    })


def product_search(request):
    q = request.GET.get('q', '').strip()
    products = Product.objects.none()
    if q:
        products = (
            Product.objects.filter(is_active=True, name_lv__icontains=q) |
            Product.objects.filter(is_active=True, name_ru__icontains=q) |
            Product.objects.filter(is_active=True, name_en__icontains=q) |
            Product.objects.filter(is_active=True, sku__icontains=q)
        ).distinct()
    return render(request, 'catalog/search.html', {'products': products, 'q': q})


# ── ATSAUKSMES ────────────────────────────────────────────────────────────────

@require_POST
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    text = request.POST.get('text', '').strip()
    try:
        rating = int(request.POST.get('rating', 5))
        rating = max(1, min(5, rating))
    except ValueError:
        rating = 5

    if not name or not text:
        messages.error(request, 'Lūdzu aizpildiet vārdu un atsauksmi.')
        return redirect('product_detail', slug=slug)

    Review.objects.create(
        product=product,
        user=request.user if request.user.is_authenticated else None,
        name=name,
        email=email,
        rating=rating,
        text=text,
        is_approved=False,
    )
    messages.success(request, 'Paldies! Jūsu atsauksme tiks publicēta pēc pārbaudes.')
    return redirect('product_detail', slug=slug)


# ── VĒLMJU SARAKSTS ───────────────────────────────────────────────────────────

def wishlist_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.user.is_authenticated:
        obj, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            obj.delete()
            in_wl = False
        else:
            in_wl = True
        count = WishlistItem.objects.filter(user=request.user).count()
    else:
        wl = request.session.get(WISHLIST_SESSION_KEY, [])
        if product.pk in wl:
            wl.remove(product.pk)
            in_wl = False
        else:
            wl.append(product.pk)
            in_wl = True
        request.session[WISHLIST_SESSION_KEY] = wl
        count = len(wl)

    if is_ajax:
        return JsonResponse({'in_wishlist': in_wl, 'count': count})
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


def wishlist_page(request):
    if request.user.is_authenticated:
        items = WishlistItem.objects.filter(user=request.user).select_related('product', 'product__brand')
        products = [i.product for i in items]
    else:
        ids = request.session.get(WISHLIST_SESSION_KEY, [])
        products = list(Product.objects.filter(pk__in=ids, is_active=True).select_related('brand'))
    return render(request, 'catalog/wishlist.html', {'products': products})


# ── SALĪDZINĀŠANA ─────────────────────────────────────────────────────────────

def compare_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    compare = request.session.get(COMPARE_SESSION_KEY, [])

    if product.pk in compare:
        compare.remove(product.pk)
        in_cmp = False
    elif len(compare) < 4:
        compare.append(product.pk)
        in_cmp = True
    else:
        if is_ajax:
            return JsonResponse({'error': 'max', 'count': len(compare)})
        messages.warning(request, 'Salīdzināšanā var pievienot ne vairāk kā 4 produktus.')
        return redirect(request.META.get('HTTP_REFERER', 'compare'))

    request.session[COMPARE_SESSION_KEY] = compare

    if is_ajax:
        return JsonResponse({'in_compare': in_cmp, 'count': len(compare)})
    return redirect(request.META.get('HTTP_REFERER', 'compare'))


def compare_page(request):
    ids = request.session.get(COMPARE_SESSION_KEY, [])
    products = list(Product.objects.filter(pk__in=ids, is_active=True)
                    .select_related('brand', 'category')
                    .prefetch_related('volumes', 'specifications'))

    all_spec_names = []
    seen = set()
    for p in products:
        for s in p.specifications.all():
            if s.name_lv not in seen:
                all_spec_names.append(s.name_lv)
                seen.add(s.name_lv)

    return render(request, 'catalog/compare.html', {
        'products': products,
        'spec_names': all_spec_names,
    })


def compare_clear(request):
    request.session[COMPARE_SESSION_KEY] = []
    return redirect(request.META.get('HTTP_REFERER', 'compare'))
