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
			'discount': 'Discount (%)',
		}
		widgets = {
            "date": DateInput(),
}