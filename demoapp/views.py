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
from django.http import FileResponse
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
Client Report Start
'''

# table one: client sale
def client_report(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('myfile')[:-1]
        myfile1 = uploaded_files[0]
        myfile2 = uploaded_files[1]
        fs = FileSystemStorage()
        if fs.exists(myfile1.name):
            fs.delete(myfile1.name)
        if fs.exists(myfile2.name):
            fs.delete(myfile2.name)
        filename1 = fs.save(myfile1.name, myfile1)
        filename2 = fs.save(myfile2.name, myfile2)
        data = analysis_client_report(filename1,filename2)
        #request.session['merged'] = data['merged']
        return render(request, 'demoapp/client_report.html', {'data':data})
    return render(request, 'demoapp/client_report.html')

from datetime import datetime, timedelta

city_to_capital = {'CH':'Abruzzo','AQ':'Abruzzo','PE':'Abruzzo','TE':'Abruzzo', 
'MT':'Basilicata', 'PZ':'Basilicata',
'CS':'Calabria', 'CZ':'Calabria', 'KR':'Calabria', 'RC':'Calabria', 'VV':'Calabria',
'AV':'Campania', 'BN':'Campania', 'CE':'Campania', 'NA':'Campania', 'SA':'Campania',
'BO':'Emilia-Romagna', 'FE':'Emilia-Romagna', 'FO':'Emilia-Romagna', 'MO':'Emilia-Romagna', 'PC':'Emilia-Romagna', 'PR':'Emilia-Romagna', 'RA':'Emilia-Romagna', 'RE':'Emilia-Romagna', 'RN':'Emilia-Romagna',
'GO':'Friuli-Venezia Giulia', 'PN':'Friuli-Venezia Giulia', 'TS':'Friuli-Venezia Giulia', 'UD':'Friuli-Venezia Giulia',
'FR':'Lazio', 'LT':'Lazio', 'RI':'Lazio', 'RM':'Lazio', 'VT':'Lazio',
'GE':'Liguria', 'IM':'Liguria', 'SP':'Liguria', 'SV':'Liguria',
'BG':'Lombardia', 'BS':'Lombardia', 'CO':'Lombardia', 'CR':'Lombardia', 'LC':'Lombardia', 'LO':'Lombardia', 'MN':'Lombardia', 'MI':'Lombardia', 'PV':'Lombardia', 'SO':'Lombardia', 'VA':'Lombardia',
'AN':'Marche', 'AP':'Marche', 'MC':'Marche', 'PS':'Marche',
'CB':'Molise', 'IS':'Molise',
'AL':'Piemonte', 'AT':'Piemonte','BI':'Piemonte', 'CN':'Piemonte','NO':'Piemonte', 'TO':'Piemonte','VB':'Piemonte', 'VC':'Piemonte',
'BA':'Puglia', 'BR':'Puglia', 'FG':'Puglia', 'LE':'Puglia', 'TA':'Puglia',
'CA':'Sardegna', 'NU':'Sardegna', 'OR':'Sardegna', 'SS':'Sardegna',
'AG':'Sicilia', 'CL':'Sicilia', 'CT':'Sicilia', 'EN':'Sicilia', 'ME':'Sicilia', 'PA':'Sicilia', 'RG':'Sicilia', 'SR':'Sicilia', 'TP':'Sicilia',
'AR':'Toscana', 'FI':'Toscana', 'GR':'Toscana', 'LI':'Toscana', 'LU':'Toscana', 'MS':'Toscana', 'PI':'Toscana', 'PT':'Toscana', 'PO':'Toscana', 'SI':'Toscana',
'BZ':'Trentino-Alto Adige', 'TN':'Trentino-Alto Adige',
'PG':'Umbria', 'TR':'Umbria',
'AO':'Valle D\'Aosta',
'BL':'Veneto', 'PD':'Veneto', 'RO':'Veneto', 'TV':'Veneto', 'VE':'Veneto', 'VI':'Veneto', 'VR':'Veneto'}

def analysis_client_report(filename1,filename2):
    print('filename1',filename1)
    print('filename2',filename2)
    file1 = os.path.join(settings.MEDIA_ROOT, filename1)
    file2 = os.path.join(settings.MEDIA_ROOT, filename2)
    print(file1)
    print(file2)
    df_client_sale = read_in_df_client_sale(file1)
    df_client_earn = read_in_df_client_earn(file2)
    grouped_sale = get_grouped_sale(df_client_sale)
    merged = get_merged(grouped_sale, df_client_earn)
    styled_df = get_styled_df(merged)
    data = {
        'merged': merged,#.to_json(orient='records'),
        'styled_df':styled_df
        } # .render()
    # os.path.join(settings.MEDIA_ROOT, '客户分析.xlsx')
    with pd.ExcelWriter(os.path.join(settings.MEDIA_ROOT, 'ClientReport.xlsx')) as writer:
        styled_df.to_excel(writer, sheet_name='ClientReport', index=False)
    return data

def read_in_df_client_sale(filename):
    df_client_sale = pd.read_html(filename)[0]
    df_client_sale.drop(df_client_sale.tail(1).index,inplace=True)
    df_client_sale.rename(columns={'客户ID号':'客户编号'},inplace=True)
    selected_columns = ['客户编号','日期','金额(€)','本次收款']
    df_client_sale = df_client_sale[selected_columns]
    return df_client_sale

def read_in_df_client_earn(filename):
    df_client_earn = pd.read_html(filename)[0]
    df_client_earn.drop(df_client_earn.tail(1).index,inplace=True)
    selected_columns = ['客户编号','客户名称', '客户经办人','城市', '省份', '分组','退货(€)','利率(%)']
    df_client_earn = df_client_earn[selected_columns]
    df_client_earn['退货(€)'].fillna(0, inplace=True)
    return df_client_earn

def get_grouped_sale(df_client_sale):
    grouped_sale = df_client_sale.groupby('客户编号').sum()
    grouped_sale['下单次数'] = df_client_sale['客户编号'].value_counts()
    grouped_sale['最近下单日期'] = grouped_sale['日期'].str[-10:]
    grouped_sale.reset_index(inplace=True)
    grouped_sale['欠款'] = grouped_sale['金额(€)'] - grouped_sale['本次收款']
    grouped_sale['欠款'] = grouped_sale['欠款'].astype(float).round(2)
    grouped_sale['欠款率%'] = grouped_sale['欠款'] /grouped_sale['金额(€)'] * 100
    grouped_sale['欠款率%'] = grouped_sale['欠款率%'].astype(float).round(2)
    return grouped_sale

def get_merged(grouped_sale, df_client_earn):
    merged = grouped_sale.merge(df_client_earn, on='客户编号', how='inner')
    # Find rows where '欠款' is greater than 0 and '退货(€)' is not equal to 0
    rows_to_update = merged[(merged['欠款'] > 0) & (merged['退货(€)'] != 0)]

    # Update '欠款' column by adding '退货(€)' value
    for index, row in rows_to_update.iterrows():
        merged.at[index, '欠款'] += row['退货(€)']

    # Update '欠款率%' column by recalculating
    rows_to_update = merged[(merged['欠款'] > 0) & (merged['欠款'] < 1)]
    for index, row in rows_to_update.iterrows():
        merged.at[index, '欠款'] = 0
        merged.at[index, '欠款率%'] = 0
    merged['利率(%)'].fillna(0, inplace=True)
    # Get Area
    merged.loc[:, '大区'] = merged['省份'].map(city_to_capital).fillna(merged['省份'])
    selected_columns = ['客户经办人','城市','省份','大区']
    merged[selected_columns] = merged[selected_columns].fillna('未知')
    selected_columns = ['客户编号','客户名称','客户经办人', '城市', '省份','大区', '分组', '下单次数', '最近下单日期', '金额(€)', '本次收款', '欠款', '欠款率%','利率(%)']
    merged = merged[selected_columns]
    return merged

def apply_color(val):
    color = 'salmon' if val != 0 else 'limegreen'
    return f'background-color: {color}'


def date_color(date_string):
    date = datetime.strptime(date_string, '%Y-%m-%d')
    ninety_days_earlier = datetime.now() - timedelta(days=90)
    if date > ninety_days_earlier:
        color = 'limegreen'
    else:
        color = 'salmon'
    return f'background-color: {color}'

def get_styled_df(merged):
    styled_df = merged.style.applymap(lambda x: apply_color(x),subset=['欠款'])
    styled_df = styled_df.applymap(lambda x: date_color(x),subset=['最近下单日期'])
    return styled_df


# with pd.ExcelWriter('客户分析.xlsx') as writer:
#    merged.to_excel(writer, sheet_name='客户报告', index=False)


def download_file(request):
    source = request.GET.get('source', None)
    # Define the path to the file you want to download
    file_path = os.path.join(settings.MEDIA_ROOT, source+'.xlsx')
    # os.path.join(settings.MEDIA_ROOT, filename1)
    # Open and serve the file for download
    file = open(file_path, 'rb')
    #with open(file_path, 'rb') as file:
    response = FileResponse(file)
    response['Content-Disposition'] = 'attachment; filename="ClientReport.xlsx"'
    return response
