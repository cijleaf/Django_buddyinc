# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0017_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='utility_last_updated',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='installation',
            name='utility_last_updated',
            field=models.DateField(blank=True, null=True),
        ),
    ]
