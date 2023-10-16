from wsgiref.simple_server import demo_app
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View, CreateView, UpdateView,DeleteView
from .models import Product
from .forms import ProductForm
# Create your views here.
def index(request):
    context = {"data":"Home Page of Django App"}
    return render(request,'demoapp/index.html', context)

class ProductsList(View):
    def get(self,request):
        items = Product.objects.all()
        context = {"data":"Dashboard Page of Django App","items":items}
        return render(request,'demoapp/product_list.html', context)


class ProductAdd(CreateView):
	model = Product
	form_class = ProductForm
	template_name = 'demoapp/product_form.html'
	success_url = reverse_lazy('product_list')

class ProductUpdate(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'demoapp/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDelete(DeleteView):
    model = Product
    template_name = 'demoapp/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')
     