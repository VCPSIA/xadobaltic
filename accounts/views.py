from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import RegisterForm, ProfileForm


def register(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Reģistrācija veiksmīga! Laipni lūgti!')
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        # Atļauj ienākšanu ar e-pastu vai lietotājvārdu
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        # Meklē pēc e-pasta
        from django.contrib.auth.models import User as DjangoUser
        user = None
        if '@' in username_or_email:
            try:
                u = DjangoUser.objects.get(email__iexact=username_or_email)
                user = authenticate(request, username=u.username, password=password)
            except DjangoUser.DoesNotExist:
                pass
        if not user:
            user = authenticate(request, username=username_or_email, password=password)
        if user:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'profile'
            return redirect(next_url)
        messages.error(request, 'Nepareizs e-pasts vai parole.')
    return render(request, 'accounts/login.html', {'next': request.GET.get('next', '')})


def user_logout(request):
    logout(request)
    return redirect('index')


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile_obj, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profils saglabāts.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile_obj, user=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def order_history(request):
    orders = request.user.orders.all().prefetch_related('items')
    return render(request, 'accounts/order_history.html', {'orders': orders})


@login_required
def order_detail_account(request, number):
    order = get_object_or_404(request.user.orders, number=number)
    return render(request, 'accounts/order_detail.html', {'order': order})
