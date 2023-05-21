#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import datetime
import logging
from pathlib import Path
import time

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from file_manager.models import Object, RootFolder, Backup


LOGGER = logging.getLogger(__name__)
ONLY_CHECK_BEFORE = timezone.now() - datetime.timedelta(days=7)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--timeout", type=int, default=60)

    def handle(self, *args, **kwargs):
        timeout = kwargs["timeout"]
        start = time.time()
        while time.time() - start < timeout:

            continue_reason = ""

            no_parent_folder_qs = Object.objects.filter(
                parent=None).exclude(path=".")
            if no_parent_folder_qs.exists():
                continue_reason = "exist file with no parent"
                for no_parent_folder in no_parent_folder_qs[0:1000]:
                    no_parent_folder.scan()

            queryset = Object.objects.filter(
                Q(last_scan__lte=ONLY_CHECK_BEFORE)
                | Q(last_scan=None)
            ).order_by("last_scan")
            if queryset.exists():
                continue_reason = "exit folder need scan"
            for obj in queryset[0:1000]:
                LOGGER.info("re scan %s", obj.absolute())
                obj.scan()

            for root_folder in RootFolder.objects.filter(object=None):
                Object.get_or_create_from_path(
                    folder=root_folder,
                    path=root_folder.absolute(),
                )

            for backup in Backup.objects.all():
                result = backup.backup(max_size=1024)
                if result is not True:
                    continue_reason = "exist back up not complete"

            if not continue_reason:
                break
            LOGGER.info("keep loop because: %s", continue_reason)
