# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0006_account_utility_service_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='utility_activated',
            field=models.CharField(null=True, blank=True, max_length=20),
        ),
    ]
