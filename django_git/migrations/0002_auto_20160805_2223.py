# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_git', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='repoinfo',
            name='local_last_updated',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='repoinfo',
            name='remote_last_updated',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
