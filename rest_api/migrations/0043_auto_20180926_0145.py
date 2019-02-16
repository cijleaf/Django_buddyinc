# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0042_auto_20180924_0307'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='agreed_to_dwolla_terms',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='account',
            name='agreed_to_fee',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='account',
            name='agreed_to_msb_terms',
            field=models.BooleanField(default=True),
        ),
    ]
