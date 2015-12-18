# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0006_auto_20151218_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='vendor',
            field=models.ForeignKey(null=True, to='invoices.Vendor'),
        ),
    ]
