# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import invoices.models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Credit',
            fields=[
                ('lineitem_ptr', models.OneToOneField(auto_created=True, to='invoices.LineItem', parent_link=True, serialize=False, primary_key=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('invoices.lineitem', invoices.models.ReverseDisplayTotalMixin),
        ),
    ]
