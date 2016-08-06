# -*- coding: utf-8 -*-
from django.db import models
from model_utils.models import TimeStampedModel


class RepoInfo(TimeStampedModel):
    full_path = models.CharField(max_length=2048)
    last_checked = models.DateTimeField(null=True, blank=True)
    last_synchronized = models.DateTimeField(null=True, blank=True)
    remote_last_updated = models.DateTimeField(null=True, blank=True)
    local_last_updated = models.DateTimeField(null=True, blank=True)
    is_clean = models.BooleanField(default=True)
    is_last_pull_success = models.BooleanField(default=True)
