# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0024_account_credit_review_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='landing_page',
            field=models.CharField(max_length=3, blank=True, default='', choices=[('CF', 'City Frame'), ('CFR', 'City Frame Report'), ('IF', 'Individual Frame'), ('IFR', 'Individual Frame Report')]),
        ),
    ]
