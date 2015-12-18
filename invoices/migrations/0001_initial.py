# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import invoices.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('address', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('date', models.DateField(null=True, blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, invoices.models.ReverseDisplayTotalMixin),
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('date', models.DateField(null=True, blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, invoices.models.DisplayTotalMixin),
        ),
        migrations.CreateModel(
            name='FixedService',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('date', models.DateField(null=True, blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, invoices.models.DisplayTotalMixin),
        ),
        migrations.CreateModel(
            name='HourlyService',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('date', models.DateField(null=True, blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('location', models.CharField(max_length=255, null=True, blank=True)),
                ('hours', models.DecimalField(decimal_places=3, max_digits=11)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, invoices.models.DisplayTotalMixin),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('date', models.DateField(null=True, blank=True)),
                ('finalized', models.BooleanField(default=False)),
                ('hourly_services_total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('fixed_services_total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('expense_total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('payment_total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('credit_total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('client', models.ForeignKey(to='invoices.Client')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('date', models.DateField(null=True, blank=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice', models.ForeignKey(to='invoices.Invoice')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, invoices.models.ReverseDisplayTotalMixin),
        ),
        migrations.CreateModel(
            name='RelatedPDF',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('pdf', models.FileField(verbose_name='PDF', upload_to=invoices.models.uuidUpload)),
                ('invoice', models.ForeignKey(to='invoices.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('phone', models.CharField(max_length=50, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('address', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='hourlyservice',
            name='invoice',
            field=models.ForeignKey(to='invoices.Invoice'),
        ),
        migrations.AddField(
            model_name='fixedservice',
            name='invoice',
            field=models.ForeignKey(to='invoices.Invoice'),
        ),
        migrations.AddField(
            model_name='expense',
            name='invoice',
            field=models.ForeignKey(to='invoices.Invoice'),
        ),
        migrations.AddField(
            model_name='credit',
            name='invoice',
            field=models.ForeignKey(to='invoices.Invoice'),
        ),
    ]
