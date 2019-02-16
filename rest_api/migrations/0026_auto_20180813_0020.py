# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0025_account_landing_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='wepay_access_token',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='account',
            name='wepay_user_id',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
