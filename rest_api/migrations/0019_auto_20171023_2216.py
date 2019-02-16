# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0018_auto_20171023_2116'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='utility_activated',
        ),
        migrations.RemoveField(
            model_name='installation',
            name='utility_activated',
        ),
    ]
