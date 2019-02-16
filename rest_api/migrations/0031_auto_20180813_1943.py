# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0030_auto_20180813_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='wepay_transaction_id',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
    ]
