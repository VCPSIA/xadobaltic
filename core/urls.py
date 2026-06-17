from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
    path('kategorija/<int:pk>/', views.nav_category_detail, name='nav_category_detail'),
    path('apakskategorija/<int:pk>/', views.nav_subcategory_products, name='nav_subcategory_products'),
]
