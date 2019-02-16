# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0026_auto_20180813_0020'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='wepay_user_id',
        ),
        migrations.AddField(
            model_name='account',
            name='wepay_account_id',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
