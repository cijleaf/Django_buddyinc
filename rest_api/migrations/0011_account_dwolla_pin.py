# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0010_auto_20160829_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='dwolla_PIN',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
