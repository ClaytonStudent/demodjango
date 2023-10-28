from wsgiref.simple_server import demo_app
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View, CreateView, UpdateView,DeleteView
from .models import Product
from .forms import ProductForm
from django.core.files.storage import FileSystemStorage
import pandas as pd
import os
from django.conf import settings
# Create your views here.
def index(request):
    context = {"data":"Home Page of Django App"}
    return render(request,'demoapp/index.html', context)

class ProductsList(View):
    def get(self,request):
        items = Product.objects.all()
        total_price = sum(item.price_with_discount for item in items)
        context = {"data":"Dashboard Page of Django App","items":items, 'total_price':total_price}
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
    
def stock_value_report(request):
    if request.method == 'POST':
        myfile1 = request.FILES['myfile1']
        myfile2 = request.FILES['myfile2']
        fs = FileSystemStorage()
        if fs.exists(myfile1.name):
            fs.delete(myfile1.name)
        if fs.exists(myfile2.name):
            fs.delete(myfile2.name)
        filename1 = fs.save(myfile1.name, myfile1)
        filename2 = fs.save(myfile2.name, myfile2)
        data = analysis_stock_value_report(filename1,filename2)
        #data = {'name1': myfile1.name, 'name2': myfile2.name}
        #request.session['df_lt_zero'] = data['df_lt_zero'].to_json(orient='records')
        #request.session['df_eq_zero'] = data['df_eq_zero'].to_json(orient='records')
        return render(request, 'demoapp/stock_value_report.html', {'data':data})
    return render(request, 'demoapp/stock_value_report.html')


def analysis_stock_value_report(filename1,filename2):
    file1 = os.path.join(settings.MEDIA_ROOT, filename1)
    file2 = os.path.join(settings.MEDIA_ROOT, filename2)
    print(file1)
    print(file2)
    df_product = get_product(file1)
    df_stock = pd.read_html(file2)[0]
    df_stock = get_stock(df_stock)
    merged_df = get_merged_df(df_stock,df_product)
    stock_value,stock_value_without_iva = get_stock_value(merged_df)
    data = {
        "txt_name": filename2.split('_')[2],
        "stock_value": stock_value,
        "stock_value_without_iva": stock_value_without_iva,
    }
    return data 

def get_product(product_file):
    df_product = pd.read_csv(product_file)
    df_product.drop(df_product.tail(1).index,inplace=True)
    df_product = df_product[['product_model','product_description','stockpile_quantity','sale_tax_rate','stock_price']]
    return df_product
def get_stock(df):
    #df = pd.read_html(stock_file)[0]
    # drop the last 1 rows
    df.drop(df.tail(1).index,inplace=True)
    # drop the under 0 stock
    df = df[df['主仓库库存']>0]
    # drop LOOK OCCHIALI EXPO
    df_expo = df[df.品名.str.contains("LOOK OCCHIALI EXPO")]
    df.drop(df_expo.index,inplace=True)
    # Drop one item
    out_index = df.index[df['型号'] == '30IOI0000002000'].to_list()[0]
    df.drop(index=out_index,inplace=True)
    # rename the columns
    df.rename(columns={'型号':'product_model'}, inplace=True)
    return df
def get_merged_df(df_stock,df_product):
    merged_df = df_stock.merge(df_product, on='product_model', how='left')
    merged_df['sale_tax_rate'].fillna(0, inplace=True)
    merged_df['sale_tax_rate'] = (merged_df['sale_tax_rate'] + 100) / 100
    return merged_df
def get_stock_value(merged_df):
    avg_stock = sum(merged_df[merged_df['成本小计']>0]['成本小计'] * merged_df[merged_df['成本小计']>0]['sale_tax_rate'])
    remain_stock = sum(merged_df[merged_df['成本小计']<=0]['小计'] * merged_df[merged_df['成本小计']<=0]['sale_tax_rate'])
    stock_value = avg_stock + remain_stock
    stock_value_without_iva = merged_df['小计'].sum()
    return int(stock_value), int(stock_value_without_iva)