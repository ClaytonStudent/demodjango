from django.db import models
from decimal import Decimal
# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    discount = models.DecimalField(max_digits=4,decimal_places=3,default=1)
    price_with_discount = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True)
    image = models.ImageField(upload_to='image/', default='image/default.jpg',null=True,blank=True)
    #slug = models.SlugField(max_length=255)
    date = models.DateField()
    note = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        # Calculate the price with discount
        #discount_percentage = Decimal('0.01')
        self.price_with_discount = self.price * self.discount #* discount_percentage

        # Call the original save method
        super(Product, self).save(*args, **kwargs)