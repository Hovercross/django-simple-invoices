# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0008_auto_20151218_1911'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='checks_payable_to',
            field=models.CharField(max_length=254, blank=True),
        ),
    ]
