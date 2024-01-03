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
        parser.add_argument("--depth", type=int, help="max scan depth")

    def handle(self, *args, **kwargs):
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
            self.scan(folder, target, kwargs["depth"])

    def scan(self, root_folder: RootFolder, scan_path: Path, remain_depth: int, parent_object=None):
        if remain_depth == 0:
            return
        for path in scan_path.iterdir():
            stat = path.stat()
            update_datetime = timestamp2datetime(stat.st_mtime)
            if path.is_dir():
                next_parent_object, _ = Object.objects.update_or_create(
                        folder=root_folder,
                        is_dir=True,
                        path=path.relative_to(root_folder.path),
                        defaults={
                            "size": stat.st_size,
                            "update_datetime": update_datetime,
                        }
                )
                self.scan(
                        root_folder=root_folder,
                        scan_path=path,
                        remain_depth=remain_depth-1,
                        parent_object=next_parent_object
                )
                continue

            file_obj = Object.objects.filter(
                folder=root_folder,
                path=path.relative_to(root_folder.path),
            ).first()
            if file_obj is None:
                file_obj = Object.objects.create(
                    folder=root_folder,
                    path=path.relative_to(root_folder.path),
                    update_datetime=update_datetime,
                    size=stat.st_size,
                    parent=parent_object,
                )
            else:
                if parent_object and not file_obj.parent:
                    file_obj.parent = parent_object
                    file_obj.save()
                if (file_obj.size, file_obj.update_datetime) == (stat.st_size, update_datetime):
                    continue
                file_obj.size = stat.st_size
                file_obj.update_datetime = update_datetime
                file_obj.md5 = ''
                file_obj.save()
