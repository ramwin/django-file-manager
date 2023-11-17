#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import datetime
import platform
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from file_manager.models import RootFolder, Object
from file_manager.utils import timestamp2datetime


class Command(BaseCommand):

    help = "scan file in folder, store info in Object model"

    def add_arguments(self, parser):
        parser.add_argument("--include", help="only scan subdire")
        parser.add_argument("--folder", type=Path, help="only scan specificed foler")

    def handle(self, *args, **kwargs):
        default_timezone = timezone.get_default_timezone()
        add_cnt = 0
        if kwargs["folder"]:
            if platform.system() == "Windows":
                queryset = RootFolder.objects.filter(windows_path=kwargs["folder"].absolute())
            elif platform.system() == "Linux":
                queryset = RootFolder.objects.filter(linux_path=kwargs["folder"].absolute())
            else:
                raise NotImplementedError
            assert queryset.exists(), f'{kwargs["folder"]} was not managed'
        else:
            queryset = RootFolder.objects.all()
        for folder in queryset:
            if kwargs.get("include"):
                target = Path(folder.path) / kwargs.get("include")
                self.stdout.write(self.style.HTTP_INFO(f"Only scan {target}"))
            else:
                target = folder.absolute()
            for path in target.rglob("*"):
                stat = path.stat()
                update_datetime = timestamp2datetime(stat.st_mtime)
                if path.is_dir():
                    Object.objects.update_or_create(
                            folder=folder,
                            is_dir=True,
                            path=path.relative_to(folder.path),
                            defaults={
                                "size": stat.st_size,
                                "update_datetime": update_datetime,
                            }
                    )
                    continue
                file_obj = Object.objects.filter(
                    folder=folder,
                    path=path.relative_to(folder.path),
                ).first()
                if file_obj is None:
                    file_obj = Object.objects.create(
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
