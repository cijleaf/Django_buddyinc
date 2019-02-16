# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0049_auto_20181005_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beneficialowner',
            name='beneficial_owner_id',
            field=models.CharField(null=True, unique=True, max_length=256, blank=True),
        ),
    ]
