# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0039_verificationdocument'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='account_status',
        ),
        migrations.AddField(
            model_name='account',
            name='funding_status',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
