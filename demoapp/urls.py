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
    path('client_check/', views.client_check, name='client_check'),
    path('download_file/', views.download_file, name='download_file'),
    path('region_sell_map_view/', views.region_sell_map_view, name='region_sell_map_view'),
    path('gls_express_report',views.gls_express_report,name='gls_express_report'),
    path('btr_express_report/',views.brt_express_report,name='btr_express_report'),
    path('boson_to_supergross/',views.boson_to_supergross,name='boson_to_supergross'),
    path('overdue_report/',views.overdue_report,name='overdue_report'),
]

