#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging

from django.core.management.base import BaseCommand
from django.utils import timezone
from file_manager.models import Backup


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--backup", type=int, help="only backup specific foler")

    def handle(self, *args, **kwargs):
        if kwargs["backup"]:
            backup_qs = Backup.objects.filter(pk=kwargs["backup"])
        else:
            backup_qs = Backup.objects.all()
        for backup in backup_qs:
            result = backup.backup()
            if result is True:
                LOGGER.info("%s backup complete", backup)
            else:
                LOGGER.info("%s backup incomplete", backup)
