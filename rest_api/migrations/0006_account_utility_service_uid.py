# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0005_remove_account_connect_preference'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='utility_service_uid',
            field=models.CharField(null=True, blank=True, max_length=20),
        ),
    ]
