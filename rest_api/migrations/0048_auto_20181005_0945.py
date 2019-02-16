# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0047_auto_20181004_2051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beneficialowner',
            name='seller',
            field=models.ForeignKey(related_name='beneficial_owners', to=settings.AUTH_USER_MODEL),
        ),
    ]
