# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0011_account_dwolla_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='seller_bill_amount',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='dwolla_PIN',
            field=models.CharField(null=True, blank=True, max_length=50),
        ),
    ]
