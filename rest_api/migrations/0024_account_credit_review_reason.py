# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0023_account_manually_set_credit'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='credit_review_reason',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
