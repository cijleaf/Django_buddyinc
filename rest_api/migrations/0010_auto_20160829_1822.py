# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0009_auto_20160824_1950'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='actual_amount',
            new_name='bill_transfer_amount',
        ),
    ]
