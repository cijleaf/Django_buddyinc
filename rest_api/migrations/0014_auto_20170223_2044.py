# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0013_installation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installation',
            name='account',
            field=models.ForeignKey(related_name='installations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='installation',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
