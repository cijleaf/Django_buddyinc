# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0028_auto_20180813_0314'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='wepay_bank_last_four',
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='wepay_bank_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='wepay_bank_status',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
