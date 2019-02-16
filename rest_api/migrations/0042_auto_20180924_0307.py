# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0041_account_funding_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='funding_status',
            field=models.CharField(max_length=200, blank=True, null=True),
        ),
    ]
