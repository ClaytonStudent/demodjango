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

'''
Stock Value Report Start
'''
def stock_value_report(request):
    if request.method == 'POST':
        print('DEBUG')
        uploaded_files = request.FILES.getlist('myfile')[:-1]
        for uploaded_file in uploaded_files:
            if '.csv' in uploaded_file.name:
                myfile1 = uploaded_file
            else:
                myfile2 = uploaded_file
        fs = FileSystemStorage()
        if fs.exists(myfile1.name):
            fs.delete(myfile1.name)
        if fs.exists(myfile2.name):
            fs.delete(myfile2.name)
        filename1 = fs.save(myfile1.name, myfile1)
        filename2 = fs.save(myfile2.name, myfile2)
        data = analysis_stock_value_report(filename1,filename2)
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
        "txt_name": filename2.split('_')[2] + '.txt',
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
    condition = df['型号'] == '30IOI0000002000'
    df = df[~condition]
    #out_index = df.index[df['型号'] == '30IOI0000002000'].to_list()[0]
    #df.drop(index=out_index,inplace=True)
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
'''
Stock Value Report End
'''


'''
Client Monthly Report Start

def client_monthly_report(request):
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
        #data = { 'filename1':filename1, 'filename2':filename2}
        data = analysis_client_monthly_report(filename1,filename2)
        return render(request, 'demoapp/client_monthly_report.html', {'data':data})
    return render(request, 'demoapp/client_monthly_report.html')

def analysis_client_monthly_report(filename1,filename2):
    file1 = os.path.join(settings.MEDIA_ROOT, filename1)
    file2 = os.path.join(settings.MEDIA_ROOT, filename2)
    df_client = pd.read_html(file1)[0]
    month_sale = df_client.tail(1)['金额(€)'].values[0] + df_client.tail(1)['退货(€)'].values[0]
    month_earn = df_client.tail(1)['本期利润'].values[0]
    month_rate = round(month_earn / month_sale * 100,2)
    print(month_sale,month_earn,month_rate)
    df_client.drop(df_client.tail(1).index,inplace=True)
    month_client_number = df_client.shape[0]
    data = {
        "month_sale": month_sale,
        "month_earn": month_earn,
        "month_rate": month_rate,
        "month_client_number": month_client_number,   
    }
    return data
'''