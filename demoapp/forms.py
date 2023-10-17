from django import forms
from .models import Product
class DateInput(forms.DateInput):
    input_type = "date"

class ProductForm(forms.ModelForm):
	class Meta:
		model = Product
		#fields =  '__all__'
		fields = ('name','date','price','discount','note','image')
		labels = {
			'name': '名称',
			'date': '日期',
			'price': '原价',
			'image': '图片',
			'note': '备注',
			'discount': '折扣',
		}
		widgets = {
            "date": DateInput(),
}