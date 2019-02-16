# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0011_account_dwolla_pin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='utility_service_uid',
            new_name='utility_meter_uid',
        ),
        migrations.RenameField(
            model_name='account',
            old_name='utility_service_id',
            new_name='utility_service_identifier',
        ),
        migrations.RemoveField(
            model_name='account',
            name='account_number',
        ),
        migrations.RemoveField(
            model_name='account',
            name='utility_api_user_uid',
        ),
        migrations.AlterField(
            model_name='account',
            name='dwolla_PIN',
            field=models.CharField(null=True, max_length=50, blank=True),
        ),
    ]
