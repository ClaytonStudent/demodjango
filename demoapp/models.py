from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    discount = models.DecimalField(max_digits=4,decimal_places=2,default=1)
    #price_with_discount = models.DecimalField(max_digits=4,decimal_places=2)
    image = models.ImageField(upload_to='image/', default='image/default.jpg',null=True,blank=True)
    slug = models.SlugField(max_length=255)
    date = models.DateField()
    note = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name