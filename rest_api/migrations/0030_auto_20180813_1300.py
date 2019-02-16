# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0029_auto_20180813_1235'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='wepay_bank_status',
            new_name='wepay_bank_state',
        ),
    ]
