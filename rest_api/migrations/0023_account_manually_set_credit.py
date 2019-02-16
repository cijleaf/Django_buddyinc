# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0022_remove_account_dwolla_pin'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='manually_set_credit',
            field=models.BooleanField(default=False),
        ),
    ]
