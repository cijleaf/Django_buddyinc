# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0032_auto_20180815_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deal',
            name='demand_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='quantity',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='deal',
            name='transaction_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
