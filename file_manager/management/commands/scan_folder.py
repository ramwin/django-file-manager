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
        add_cnt = 0
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
                file_obj = File.objects.filter(
                    folder=folder,
                    path=path.relative_to(folder.path),
                ).first()
                if file_obj is None:
                    file_obj = File.objects.create(
                        folder=folder,
                        path=path.relative_to(folder.path),
                        update_datetime=update_datetime,
                        size=stat.st_size
                    )
                    add_cnt += 1
                else:
                    if (file_obj.size, file_obj.update_datetime) == (stat.st_size, update_datetime):
                        continue
                    file_obj.size = stat.st_size
                    file_obj.update_datetime = update_datetime
                    file_obj.md5 = ''
                    file_obj.save()

        self.stdout.write(self.style.HTTP_INFO(f"{add_cnt} file added"))
