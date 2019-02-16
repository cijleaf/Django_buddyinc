# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0015_deal_installation'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='buyer_automatch',
            field=models.BooleanField(default=False),
        ),
    ]
