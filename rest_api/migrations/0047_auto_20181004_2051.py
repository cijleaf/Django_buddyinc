# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0046_beneficialowner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='beneficialowner',
            old_name='beneficial_status',
            new_name='verification_status',
        ),
        migrations.AlterField(
            model_name='sellerbusinessinformation',
            name='seller',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='business_information_seller'),
        ),
    ]
