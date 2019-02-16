# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0008_auto_20160824_1933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='credit_to_sell_percent',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
