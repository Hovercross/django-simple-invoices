# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-12-25 00:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0012_auto_20171224_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credit',
            name='position',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='expense',
            name='position',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='fixedservice',
            name='position',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='hourlyservice',
            name='position',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='payment',
            name='position',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='relatedpdf',
            name='position',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
    ]
