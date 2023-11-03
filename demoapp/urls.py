from pathlib import Path
from unicodedata import name
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.index,name="index"),
    path("product_list/", views.ProductsList.as_view(),name="product_list"),
    path("product_add/", views.ProductAdd.as_view(),name="product_add"),
    path("product_update/<int:pk>/", views.ProductUpdate.as_view(),name="product_update"),
    path("product_delete/<int:pk>/", views.ProductDelete.as_view(),name="product_delete"),
    path('stock_value_report/', views.stock_value_report, name='stock_value_report'),
    path('client_report/', views.client_report, name='client_report'),
    path('download_file/', views.download_file, name='download_file'),
    path('region_sell_map_view/', views.region_sell_map_view, name='region_sell_map_view'),
]

