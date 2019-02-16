# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0044_auto_20181001_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='dwolla_customer_type',
            field=models.CharField(max_length=50, default='unverified'),
        ),
        migrations.AddField(
            model_name='sellerbusinessinformation',
            name='controller_zip_code',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
    ]
