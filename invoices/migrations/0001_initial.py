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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('total', models.DecimalField(max_digits=20, decimal_places=2)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, invoices.models.ReverseDisplayTotalMixin),
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('total', models.DecimalField(max_digits=20, decimal_places=2)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, invoices.models.DisplayTotalMixin),
        ),
        migrations.CreateModel(
            name='FixedService',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('total', models.DecimalField(max_digits=20, decimal_places=2)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, invoices.models.DisplayTotalMixin),
        ),
        migrations.CreateModel(
            name='HourlyService',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('total', models.DecimalField(max_digits=20, decimal_places=2)),
                ('location', models.CharField(blank=True, null=True, max_length=255)),
                ('hours', models.DecimalField(max_digits=11, decimal_places=3)),
                ('rate', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, invoices.models.DisplayTotalMixin),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('finalized', models.BooleanField(default=False)),
                ('hourly_services_total', models.DecimalField(max_digits=20, default=0, decimal_places=2)),
                ('fixed_services_total', models.DecimalField(max_digits=20, default=0, decimal_places=2)),
                ('expense_total', models.DecimalField(max_digits=20, default=0, decimal_places=2)),
                ('payment_total', models.DecimalField(max_digits=20, default=0, decimal_places=2)),
                ('credit_total', models.DecimalField(max_digits=20, default=0, decimal_places=2)),
                ('total_charges', models.DecimalField(max_digits=20, default=0, decimal_places=2)),
                ('total_credits', models.DecimalField(max_digits=20, default=0, decimal_places=2)),
                ('total', models.DecimalField(max_digits=20, default=0, decimal_places=2)),
                ('client', models.ForeignKey(to='invoices.Client')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('total', models.DecimalField(max_digits=20, decimal_places=2)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('pdf', models.FileField(upload_to=invoices.models.uuidUpload, verbose_name='PDF')),
                ('invoice', models.ForeignKey(to='invoices.Invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('checks_payable_to', models.CharField(blank=True, max_length=254)),
                ('address', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='invoice',
            name='vendor',
            field=models.ForeignKey(to='invoices.Vendor'),
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
