# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0048_auto_20181005_0945'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='beneficialowner',
            name='certification_status',
        ),
        migrations.AddField(
            model_name='account',
            name='certification_status',
            field=models.CharField(max_length=50, default='uncertified'),
        ),
    ]
