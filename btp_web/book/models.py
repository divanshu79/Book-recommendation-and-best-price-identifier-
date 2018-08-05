from __future__ import unicode_literals

from django.db import models
from decimal import Decimal

class user_info(models.Model):
    uid = models.CharField(max_length=250)
    name=models.CharField(max_length=250)
    author = models.CharField(max_length=50,null=True)
    book_name = models.CharField(max_length=250)
    amazon_link = models.CharField(max_length=250,null=True)
    picture= models.CharField(max_length=250,null=True)
    # book_picture= models.CharField(max_length=250,null=True)
    rating=models.DecimalField(default=Decimal('0.00'), max_digits=5, decimal_places=2,null=True)
    global_rating=models.DecimalField(default=Decimal('0.00'), max_digits=5, decimal_places=2,null=True)

    def __str__(self):
        return self.name
class ordering(models.Model):
	book_name  =  models.CharField(max_length=250)
	review_rating = models.DecimalField(default=Decimal('0.00'), max_digits=5, decimal_places=2,null=True)
	amazon_rating = models.DecimalField(default=Decimal('0.00'), max_digits=5, decimal_places=2,null=True)

	def __str__(self):
		return self.id

