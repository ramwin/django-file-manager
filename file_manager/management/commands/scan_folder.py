#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from file_manager.models import Folder, File


class Command(BaseCommand):

    help = "scan file in folder, store info in File model"

    def add_arguments(self, parser):
        parser.add_argument("--include", help="only scan subdire")

    def handle(self, *args, **kwargs):
        default_timezone = timezone.get_default_timezone()
        for folder in Folder.objects.all():
            if kwargs.get("include"):
                target = Path(folder.path) / kwargs.get("include")
                self.stdout.write(self.style.HTTP_INFO(f"Only scan {target}"))
            else:
                target = Path(folder.path)
            for path in target.rglob("*"):
                if path.is_dir():
                    continue
                stat = path.stat()
                update_datetime = datetime.datetime.fromtimestamp(stat.st_mtime).astimezone(
                    default_timezone,
                )
                File.objects.update_or_create(
                    folder=folder,
                    path=path.relative_to(folder.path),
                    defaults={
                        "size": stat.st_size,
                        "update_datetime": update_datetime,
                    },
                )
