from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/<str:number>/', views.order_success, name='order_success'),
]
