# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0040_auto_20180922_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='funding_balance',
            field=models.DecimalField(blank=True, max_digits=10, decimal_places=2, null=True),
        ),
    ]
