# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ordering',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('book_name', models.CharField(max_length=250)),
                ('review_rating', models.DecimalField(default=Decimal('0.00'), null=True, max_digits=5, decimal_places=2)),
                ('amazon_rating', models.DecimalField(default=Decimal('0.00'), null=True, max_digits=5, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='user_info',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=250)),
                ('name', models.CharField(max_length=250)),
                ('author', models.CharField(max_length=50, null=True)),
                ('book_name', models.CharField(max_length=250)),
                ('amazon_link', models.CharField(max_length=250, null=True)),
                ('picture', models.CharField(max_length=250, null=True)),
                ('book_picture', models.CharField(max_length=250, null=True)),
                ('rating', models.DecimalField(default=Decimal('0.00'), null=True, max_digits=5, decimal_places=2)),
                ('global_rating', models.DecimalField(default=Decimal('0.00'), null=True, max_digits=5, decimal_places=2)),
            ],
        ),
    ]
