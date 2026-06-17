from django.urls import path
from . import views

urlpatterns = [
    path('', views.selector, name='selector'),
    path('api/brands/', views.api_brands, name='api_brands'),
    path('api/models/', views.api_models, name='api_models'),
    path('api/modifications/', views.api_modifications, name='api_modifications'),
    path('api/products/', views.api_products, name='api_products'),
]
