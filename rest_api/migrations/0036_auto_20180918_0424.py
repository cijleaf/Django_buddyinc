# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0035_actionlog_sellerbusinessinformation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionlog',
            name='funding_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
