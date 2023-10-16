from wsgiref.simple_server import demo_app
from django.shortcuts import render
from django.views.generic import View
from .models import Product
# Create your views here.
def index(request):
    context = {"data":"Home Page of Django App"}
    return render(request,'demoapp/index.html', context)

class ProductsList(View):
    def get(self,request):
        items = Product.objects.all()
        context = {"data":"Dashboard Page of Django App","items":items}
        return render(request,'demoapp/product_list.html', context)
