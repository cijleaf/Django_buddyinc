# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0043_auto_20180926_0145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='utility_last_updated',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
