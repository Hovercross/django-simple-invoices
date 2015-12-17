# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import invoices.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('address', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date', models.DateField(null=True, blank=True)),
                ('finalized', models.BooleanField(default=False)),
                ('client', models.ForeignKey(to='invoices.Client')),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('date', models.DateField(null=True, blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RelatedPDF',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('pdf', models.FileField(upload_to=invoices.models.uuidUpload, verbose_name='PDF')),
                ('invoice', models.ForeignKey(to='invoices.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('lineitem_ptr', models.OneToOneField(serialize=False, parent_link=True, auto_created=True, to='invoices.LineItem', primary_key=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('invoices.lineitem',),
        ),
        migrations.CreateModel(
            name='FixedService',
            fields=[
                ('lineitem_ptr', models.OneToOneField(serialize=False, parent_link=True, auto_created=True, to='invoices.LineItem', primary_key=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('invoices.lineitem',),
        ),
        migrations.CreateModel(
            name='HourlyService',
            fields=[
                ('lineitem_ptr', models.OneToOneField(serialize=False, parent_link=True, auto_created=True, to='invoices.LineItem', primary_key=True)),
                ('location', models.CharField(max_length=255, null=True, blank=True)),
                ('hours', models.DecimalField(decimal_places=3, max_digits=11)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('invoices.lineitem',),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('lineitem_ptr', models.OneToOneField(serialize=False, parent_link=True, auto_created=True, to='invoices.LineItem', primary_key=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('invoices.lineitem',),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='invoice',
            field=models.ForeignKey(to='invoices.Invoice'),
        ),
        migrations.AddField(
            model_name='lineitem',
            name='polymorphic_ctype',
            field=models.ForeignKey(null=True, editable=False, to='contenttypes.ContentType', related_name='polymorphic_invoices.lineitem_set+'),
        ),
    ]
