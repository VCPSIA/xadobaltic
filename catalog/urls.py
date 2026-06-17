from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='catalog'),
    path('search/', views.product_search, name='product_search'),
    path('brands/', views.brand_list, name='brand_list'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<slug:slug>/review/', views.add_review, name='add_review'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('wishlist/toggle/<int:pk>/', views.wishlist_toggle, name='wishlist_toggle'),
    path('compare/', views.compare_page, name='compare'),
    path('compare/toggle/<int:pk>/', views.compare_toggle, name='compare_toggle'),
    path('compare/clear/', views.compare_clear, name='compare_clear'),
]
