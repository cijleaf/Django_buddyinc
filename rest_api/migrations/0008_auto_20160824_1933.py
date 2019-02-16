# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0007_account_utility_activated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='utility_activated'
        ),
        migrations.AddField(
            model_name='account',
            name='utility_activated',
            field=models.BooleanField(default=False),
        ),
    ]
