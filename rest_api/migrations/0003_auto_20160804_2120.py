# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0002_account_average_monthly_credit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='is_verified',
        ),
        migrations.RemoveField(
            model_name='account',
            name='verified_at',
        ),
    ]
