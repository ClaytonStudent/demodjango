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
from PyPDF2 import PdfReader
from datetime import date
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
        myfile1 = request.FILES['myfile1']
        myfile2 = request.FILES['myfile2']
       # uploaded_files = request.FILES.getlist('myfile')[:-1]
       # for uploaded_file in uploaded_files:
       #     if '.csv' in uploaded_file.name:
       #         myfile1 = uploaded_file
       #     else:
       #         myfile2 = uploaded_file
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
        "date": filename2.split('_')[2],
        "stock_value": stock_value,
        "stock_value_without_iva": stock_value_without_iva,
    }
    # Specify the path to the text file
    file_name = "StockValue.txt"  # Replace with your desired file path
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    # Open the file for writing
    with open(file_path, 'w') as file:
        # Write the data to the file
        for key, value in data.items():
            file.write(f"{key}: {value}\n")
    file.close()
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
        #uploaded_files = request.FILES.getlist('myfile')[:-1]
        #myfile1 = uploaded_files[0]
        #myfile2 = uploaded_files[1]
        myfile1 = request.FILES['myfile1']
        myfile2 = request.FILES['myfile2']
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
'BO':'Emilia-Romagna', 'FE':'Emilia-Romagna', 'FO':'Emilia-Romagna', 'MO':'Emilia-Romagna', 'PC':'Emilia-Romagna', 'PR':'Emilia-Romagna', 'RA':'Emilia-Romagna', 'RE':'Emilia-Romagna', 'RN':'Emilia-Romagna', 'FC':'Emilia-Romagna',
'GO':'Friuli-Venezia Giulia', 'PN':'Friuli-Venezia Giulia', 'TS':'Friuli-Venezia Giulia', 'UD':'Friuli-Venezia Giulia',
'FR':'Lazio', 'LT':'Lazio', 'RI':'Lazio', 'RM':'Lazio', 'VT':'Lazio',
'GE':'Liguria', 'IM':'Liguria', 'SP':'Liguria', 'SV':'Liguria',
'BG':'Lombardia', 'BS':'Lombardia', 'CO':'Lombardia', 'CR':'Lombardia', 'LC':'Lombardia', 'LO':'Lombardia', 'MN':'Lombardia', 'MI':'Lombardia', 'PV':'Lombardia', 'SO':'Lombardia', 'VA':'Lombardia','MB':'Lombardia',
'AN':'Marche', 'AP':'Marche', 'MC':'Marche', 'PS':'Marche','PU':'Marche', 'FM':'Marche',
'CB':'Molise', 'IS':'Molise',
'AL':'Piemonte', 'AT':'Piemonte','BI':'Piemonte', 'CN':'Piemonte','NO':'Piemonte', 'TO':'Piemonte','VB':'Piemonte', 'VC':'Piemonte',
'BA':'Puglia', 'BR':'Puglia', 'FG':'Puglia', 'LE':'Puglia', 'TA':'Puglia', 'BT':'Puglia',
'CA':'Sardegna', 'NU':'Sardegna', 'OR':'Sardegna', 'SS':'Sardegna', 'SU':'Sardegna', 'OT':'Sardegna', 'CI':'Sardegna',
'AG':'Sicilia', 'CL':'Sicilia', 'CT':'Sicilia', 'EN':'Sicilia', 'ME':'Sicilia', 'PA':'Sicilia', 'RG':'Sicilia', 'SR':'Sicilia', 'TP':'Sicilia',
'AR':'Toscana', 'FI':'Toscana', 'GR':'Toscana', 'LI':'Toscana', 'LU':'Toscana', 'MS':'Toscana', 'PI':'Toscana', 'PT':'Toscana', 'PO':'Toscana', 'SI':'Toscana',
'BZ':'Trentino-Alto Adige', 'TN':'Trentino-Alto Adige',
'PG':'Umbria', 'TR':'Umbria',
'AO':'Valle D\'Aosta',
'BL':'Veneto', 'PD':'Veneto', 'RO':'Veneto', 'TV':'Veneto', 'VE':'Veneto', 'VI':'Veneto', 'VR':'Veneto',
'MX':'EE', 'AU':'EE', 'BE':'EE'
}

def analysis_client_report(filename1,filename2):
    file1 = os.path.join(settings.MEDIA_ROOT, filename1)
    file2 = os.path.join(settings.MEDIA_ROOT, filename2)
    print(file1)
    print(file2)
    df_client_sale = read_in_df_client_sale(file1)
    df_client_earn = read_in_df_client_earn(file2)
    sales_by_month, month_names = get_sale_by_month(df_client_sale)
    grouped_sale = get_grouped_sale(df_client_sale,sales_by_month)
    merged = get_merged(grouped_sale, df_client_earn,month_names)
    styled_df = get_styled_df(merged,month_names)
    handler_area_sell,handler_sell,area_sell = add_handler_area_sell(merged)
    with pd.ExcelWriter(os.path.join(settings.MEDIA_ROOT, 'ClientReport.xlsx')) as writer:
        styled_df.to_excel(writer, sheet_name='客户销售', index=False)
        handler_area_sell.to_excel(writer, sheet_name='推销员-大区-销售',index=False)
        handler_sell.to_excel(writer, sheet_name='推销员-销售',index=False)
        area_sell.to_excel(writer, sheet_name='大区-销售',index=False)
    data = {
        'merged': merged,#.to_json(orient='records'),
        'styled_df':styled_df
        } 
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
    selected_columns = ['客户编号','客户名称', '客户经办人','手机','税号','地址','城市', '省份', '分组','退货(€)','利率(%)']
    df_client_earn = df_client_earn[selected_columns]
    df_client_earn['退货(€)'].fillna(0, inplace=True)
    return df_client_earn

def get_sale_by_month(df_client_sale):
    df_client_sale['月份'] = df_client_sale['日期'].str[5:7]
    sales_by_month = df_client_sale.groupby(['客户编号', '月份'])['金额(€)'].sum().unstack().reset_index()
    sales_by_month.fillna(0, inplace=True)
    month_names = list(sales_by_month.columns.values[1:])
    return sales_by_month, month_names


def get_grouped_sale(df_client_sale,sales_by_month):
    grouped_sale = df_client_sale.groupby('客户编号').sum()
    grouped_sale['下单次数'] = df_client_sale['客户编号'].value_counts()
    grouped_sale['最近下单日期'] = grouped_sale['日期'].str[-10:]
    grouped_sale.reset_index(inplace=True)
    grouped_sale['欠款'] = grouped_sale['金额(€)'] - grouped_sale['本次收款']
    grouped_sale['欠款'] = grouped_sale['欠款'].astype(float).round(2)
    grouped_sale['欠款率(%)'] = grouped_sale['欠款'] /grouped_sale['金额(€)'] * 100
    grouped_sale['欠款率(%)'] = grouped_sale['欠款率(%)'].astype(float).round(2)
    grouped_sale = grouped_sale.merge(sales_by_month, on='客户编号', how='inner')
    return grouped_sale

def get_merged(grouped_sale, df_client_earn,month_names):
    merged = grouped_sale.merge(df_client_earn, on='客户编号', how='inner')
    # Find rows where '欠款' is greater than 0 and '退货(€)' is not equal to 0
    rows_to_update = merged[(merged['欠款'] > 0) & (merged['退货(€)'] != 0)]

    # Update '欠款' column by adding '退货(€)' value
    for index, row in rows_to_update.iterrows():
        merged.at[index, '欠款'] += row['退货(€)']

    # Update '欠款率(%)' column by recalculating
    rows_to_update = merged[(merged['欠款'] > 0) & (merged['欠款'] < 1)]
    for index, row in rows_to_update.iterrows():
        merged.at[index, '欠款'] = 0
        merged.at[index, '欠款率(%)'] = 0
    merged['利率(%)'].fillna(0, inplace=True)
    # Get Area
    merged.loc[:, '大区'] = merged['省份'].map(city_to_capital).fillna(merged['省份'])
    selected_columns = ['客户经办人','城市','省份','大区']
    merged[selected_columns] = merged[selected_columns].fillna('未知')
    merged['大区'] = merged['大区'].replace('未知','Campania')
    selected_columns = ['客户编号','客户名称','客户经办人','手机','税号','地址', '城市', '省份','大区', '分组', '下单次数', '最近下单日期', '金额(€)', '本次收款', '欠款', '欠款率(%)','利率(%)'] + month_names
    merged = merged[selected_columns]
    #name_match = {'本次收款':'收款','金额(€)':'金额',}
    #merged.rename(columns=name_match, inplace=True)
    return merged


def add_handler_area_sell(merged):
    handler_area_sell =merged.groupby(['客户经办人', '大区'])['金额(€)'].sum().reset_index().sort_values('金额(€)', ascending=False)
    handler_sell = merged.groupby('客户经办人')['金额(€)'].sum().reset_index().sort_values('金额(€)', ascending=False)
    area_sell = merged.groupby('大区')['金额(€)'].sum().reset_index().sort_values('金额(€)', ascending=False)
    return handler_area_sell, handler_sell, area_sell

def month_color(val):
    color = 'limegreen' if val > 0 else 'none' # none transparent
    return f'background-color: {color}'

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

def debt_rate_color(val):
    color = 'salmon' if val > 50 else 'limegreen'
    return f'background-color: {color}'

def earning_rate_color(val):
    color = 'salmon' if val < 20 else 'limegreen'
    return f'background-color: {color}'

def get_styled_df(merged,month_names):
    styled_df = merged.style.applymap(lambda x: apply_color(x),subset=['欠款'])
    styled_df = styled_df.applymap(lambda x: debt_rate_color(x),subset=['欠款率(%)'])
    styled_df = styled_df.applymap(lambda x: earning_rate_color(x),subset=['利率(%)'])
    styled_df = styled_df.applymap(lambda x: date_color(x),subset=['最近下单日期'])
    styled_df = styled_df.applymap(lambda x: month_color(x),subset=month_names)
    return styled_df

def download_file(request):
    source = request.GET.get('source', None)
    print(source)
    # Define the path to the file you want to download
    file_path = os.path.join(settings.MEDIA_ROOT, source)
    # os.path.join(settings.MEDIA_ROOT, filename1)
    # Open and serve the file for download
    file = open(file_path, 'rb')
    #with open(file_path, 'rb') as file:
    response = FileResponse(file)
    #response['Content-Disposition'] = 'attachment; filename="{source}"'
    response['Content-Disposition'] = f'attachment; filename="{source}"'
    return response


'''
Region Sell Map View
'''
from django.shortcuts import render
import json,csv

def region_sell_map_view(request):
    csv_file = os.path.join(settings.MEDIA_ROOT, 'area_sell.csv')
    data = [['Code','Label', 'Sales', 'Population']]
    sale_population = []
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if present
        for row in reader:
            # Assuming the CSV has two columns: 'Country' and 'sales'
            code, country, sales, population = row
            formatted_sales = "{:,}".format(int(float(sales))) + '€      '
            formatted_population = "{:,}".format(int(float(population)))
            data.append([code, country,int(float(sales)),int(float(population))])
            sale_population.append([code,country,formatted_sales, formatted_population])
    context= {'array': json.dumps(data), 'data':data[1:],'sale_population':sale_population }
    return render(request, 'demoapp/region_sell_map_view.html',context)

'''
Express Info
'''
def gls_express_report(request):
    if request.method == 'POST':
        print('DEBUG')
        myfile1 = request.FILES['myfile1']
        myfile2 = request.FILES['myfile2']
        fs = FileSystemStorage()
        if fs.exists(myfile1.name):
            fs.delete(myfile1.name)
        if fs.exists(myfile2.name):
            fs.delete(myfile2.name)
        filename1 = fs.save(myfile1.name, myfile1)
        filename2 = fs.save(myfile2.name, myfile2)
        data = gls_save_df(myfile1.name,myfile2.name)
        return render(request, 'demoapp/gls_express_report.html', {'data':data})
    return render(request, 'demoapp/gls_express_report.html')

def gls_save_df(filename1,filename2):
    file1 = os.path.join(settings.MEDIA_ROOT, filename1)
    file2 = os.path.join(settings.MEDIA_ROOT, filename2)
    merged_df = gls_generate_df(file1,file2)
    with pd.ExcelWriter(os.path.join(settings.MEDIA_ROOT, 'GLS.xlsx')) as writer:
        merged_df.to_excel(writer, sheet_name='快递报告', index=False) 
    data = {}
    return data

def gls_generate_df(file1,file2):
    reader = PdfReader(file1)
    wholeline=[]
    for page in reader.pages:
            contents = page.extract_text().split('\n')   
            for i,v in enumerate(contents):
                    if len(v) > 100 and v[:4]=='2024':
                            wholeline.append([v[-8:],v[11:22]])
    df_pdf = pd.DataFrame(wholeline,columns=['发票单号','快递单号'])
    converter_columns = ['销售单','发票单号']
    converters = {c:lambda x: str(x) for c in converter_columns}
    df = pd.read_html(file2,converters=converters)[0]
    df.drop(df.tail(1).index,inplace=True)
    selected_columns = ['客户','收付款方式','金额(€)','销售单','发票单号','经办人']
    df = df[selected_columns]
    merged_df = df.merge(df_pdf, on='发票单号', how='right')
    return merged_df

'''
BRT Express 
'''
def brt_express_report(request):
    if request.method == 'POST':
        myfile1 = request.FILES['myfile1']
        myfile2 = request.FILES['myfile2']
        fs = FileSystemStorage()
        if fs.exists(myfile1.name):
            fs.delete(myfile1.name)
        if fs.exists(myfile2.name):
            fs.delete(myfile2.name)
        fs.save(myfile1.name, myfile1)
        fs.save(myfile2.name, myfile2)
        data = brt_save_df(myfile1.name,myfile2.name)
        return render(request, 'demoapp/brt_express_report.html', {'data':data})
    return render(request, 'demoapp/brt_express_report.html')

def brt_save_df(filename1,filename2):
    file1 = os.path.join(settings.MEDIA_ROOT, filename1)
    file2 = os.path.join(settings.MEDIA_ROOT, filename2)
    wholeline,date_name = brt_content_from_pdf(file1)
    df_xls,df = brt_merge_df(file2,wholeline)
    df = brt_fillna_df(df,df_xls)
    df = brt_add_date_df(df,date_name)
    with pd.ExcelWriter(os.path.join(settings.MEDIA_ROOT, 'BRT.xlsx')) as writer:
        df.to_excel(writer, sheet_name=date_name, index=False) 
    data = {'date_name':date_name}
    return data

def brt_content_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    wholeline=[]
    date_name = date.today().strftime("%d_%m_%Y")
    for page in reader.pages:
        contents = page.extract_text().split('\n')        
        for i,v in enumerate(contents):
            if (v == "Tipo Servizio"):
                if (contents[i-5] == "EUR"):
                    wholeline.append([contents[i-12], contents[i-7], contents[i-6].replace('.','').replace(',','.')])
                else:
                    wholeline.append([contents[i-9]])
            if 'Del' in v:
                        date_name = contents[i+1].replace('/','_')
    return wholeline,date_name

def brt_merge_df(xls_name,wholeline):
    print(xls_name)
    df_xls = pd.read_html(xls_name,converters={'销售单': str,'发票单号':str})[0]
    print(df_xls)
    df_xls.drop(df_xls.tail(1).index,inplace=True)
    df_xls.rename(columns={"客户": "client", "销售单":"order_id", "经办人":"agent",'金额(€)':'euro','发票单号':'invoice_id','收付款方式':'transport'  }, inplace=True)
    df_xls['client']= df_xls['client'].str.rstrip()
    df_xls['client']= df_xls['client'].str.lstrip()

    df_xlsx = pd.DataFrame(wholeline,columns=['client','transport','euro'])
    df_xlsx['client']= df_xlsx['client'].str.rstrip()
    df_xlsx['client']= df_xlsx['client'].str.lstrip()
    df_xlsx['euro'] = df_xlsx['euro'].astype(float)
    df = pd.merge(df_xlsx, df_xls[['client','euro','agent','order_id','invoice_id']], on ='client', how ="left")
    return df_xls,df

def brt_fillna_df(df,df_xls):
    df['euro_x'].fillna(df['euro_y'], inplace=True)
    df['euro'] = df['euro_x']
    df = df.drop(['euro_x', 'euro_y'], axis=1)


    # Assuming you have DataFrames df and df_xls with columns 'client', 'transport', 'agent', 'order_id', 'euro'
    # Merge the two DataFrames based on the 'euro' column for 'order_id'
    merged_df_order_id = pd.merge(df[['client', 'transport', 'agent', 'order_id', 'euro']],
                                df_xls[['euro', 'order_id']],
                                on='euro',
                                how='left',
                                suffixes=('_df', '_xls'))

    # Fill NaN values in 'order_id_df' with values from 'order_id_xls'
    merged_df_order_id['order_id_df'].fillna(merged_df_order_id['order_id_xls'], inplace=True)

    # Drop the temporary 'order_id_xls' column if needed
    merged_df_order_id = merged_df_order_id.drop('order_id_xls', axis=1)

    # Update the original df DataFrame with the filled 'order_id' values
    df['order_id'] = merged_df_order_id['order_id_df']

    # Merge the two DataFrames based on the 'euro' column for 'agent'
    merged_df_agent = pd.merge(df[['client', 'transport', 'agent', 'order_id', 'euro']],
                            df_xls[['euro', 'agent']],
                            on='euro',
                            how='left',
                            suffixes=('_df', '_xls'))

    # Fill NaN values in 'agent_df' with values from 'agent_xls'
    merged_df_agent['agent_df'].fillna(merged_df_agent['agent_xls'], inplace=True)

    # Drop the temporary 'agent_xls' column if needed
    merged_df_agent = merged_df_agent.drop('agent_xls', axis=1)

    # Update the original df DataFrame with the filled 'agent' values
    df['agent'] = merged_df_agent['agent_df']

    # Merge the two DataFrames based on the 'euro' column for 'transport'
    merged_df_transport = pd.merge(df[['client', 'transport', 'agent', 'order_id', 'euro']],
                                df_xls[['euro', 'transport']],
                                on='euro',
                                how='left',
                                suffixes=('_df', '_xls'))

    # Fill NaN values in 'transport_df' with values from 'transport_xls'
    merged_df_transport['transport_df'].fillna(merged_df_transport['transport_xls'], inplace=True)
    

    # Drop the temporary 'transport_xls' column if needed
    merged_df_transport = merged_df_transport.drop('transport_xls', axis=1)

    # Update the original df DataFrame with the filled 'transport' values and convert to string
    df['transport'] = merged_df_transport['transport_df'].astype(str).str.rstrip('.0')
    df['transport'] = df['transport'].str.replace('nan','')
    return df

def brt_add_date_df(df,date_name):
    df.rename(columns={'client':'客户','transport':'收付款方式','euro':'金额(€)','order_id':'销售单','invoice_id':'发票单号','agent':'经办人'}, inplace=True)
    df['日期'] = date_name.replace('_','/')
    df = df[['日期','客户','收付款方式','金额(€)','销售单','发票单号','经办人']]
    return df