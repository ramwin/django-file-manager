#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


from pathlib import Path
from django.core.management.base import BaseCommand
import logging


from file_manager.models import Object, RootFolder, Backup


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        while True:
            qs = Object.objects.filter(path__contains="\\")
            if not qs.exists():
                return
            for i in qs[0:1000]:
                unix_object = Object.objects.filter(
                    path=Path(i.path).as_posix(),
                    folder=i.folder,
                ).first()
                if unix_object is None:
                    i.path = Path(i.path).as_posix()
                    i.save()
                    continue
                if not unix_object.md5 and i.md5:
                    unix_object.md5 = i.md5
                    unix_object.save()
                assert unix_object.id != i.id
                i.delete()
            LOGGER.info("delete 1000 duplicate data, last one was: %s", i)
