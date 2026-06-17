from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from catalog.models import Product, ProductVolume
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    volume_id = request.POST.get('volume_id')
    quantity = int(request.POST.get('quantity', 1))

    if volume_id:
        volume = get_object_or_404(ProductVolume, id=volume_id, product=product, is_active=True)
    else:
        volume = product.default_volume()
        if not volume:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Nav tilpumu'}, status=400)
            return redirect('product_detail', slug=product.slug)

    cart.add(product, volume, quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': len(cart), 'message': 'Pievienots grozam'})
    return redirect('cart_detail')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    volume_id = request.POST.get('volume_id')
    quantity = int(request.POST.get('quantity', 1))
    cart.update(product_id, volume_id, quantity)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': len(cart)})
    return redirect('cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    volume_id = request.POST.get('volume_id')
    cart.remove(product_id, volume_id)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'cart_count': len(cart)})
    return redirect('cart_detail')
