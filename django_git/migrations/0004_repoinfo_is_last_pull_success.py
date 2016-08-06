# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_git', '0003_repoinfo_last_checked'),
    ]

    operations = [
        migrations.AddField(
            model_name='repoinfo',
            name='is_last_pull_success',
            field=models.BooleanField(default=True),
        ),
    ]
