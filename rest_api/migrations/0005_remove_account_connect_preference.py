# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0004_auto_20160805_1846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='connect_preference',
        ),
    ]
