from pathlib import Path
from unicodedata import name
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.index,name="index"),
    path("product_list/", views.ProductsList.as_view(),name="product_list"),
]

