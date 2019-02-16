# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0037_auto_20180920_1417'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='seller_bill_amount',
        ),
    ]
