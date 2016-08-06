# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_git', '0002_auto_20160805_2223'),
    ]

    operations = [
        migrations.AddField(
            model_name='repoinfo',
            name='last_checked',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
