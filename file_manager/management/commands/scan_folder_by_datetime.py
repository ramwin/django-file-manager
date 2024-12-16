#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from django_commands.utils import iter_large_queryset

from file_manager.models import Object


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "scan all folders according it's ctime"

    def handle(self, *args, **kwargs) -> None:
        now = timezone.now()
        queryset = Object.objects.filter(is_dir=True, last_scan__lt=now)
        for sub_queryset in iter_large_queryset(queryset):
            obj: Object
            for obj in sub_queryset:
                if not obj.absolute().exists():
                    continue
                if obj.absolute().stat().st_mtime > obj.last_scan.timestamp():
                    LOGGER.info("rescan folder: %s", obj)
                    obj.scan(recursive=False)
