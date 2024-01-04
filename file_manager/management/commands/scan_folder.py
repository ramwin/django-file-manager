#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import datetime
import logging
import platform
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from file_manager.models import RootFolder, Object
from file_manager.utils import timestamp2datetime, to_unix_str


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "scan file in folder, store info in Object model"

    def add_arguments(self, parser):
        parser.add_argument("--include", help="only scan subdire")
        parser.add_argument("--folder", type=Path, help="only scan specificed foler")
        parser.add_argument("--depth", type=int, help="max scan depth", default=-1)

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
            parent_object = None
            target: Path
            if kwargs.get("include"):
                target = Path(folder.path) / kwargs.get("include")
            else:
                target = folder.absolute()
            if target.exists():
                if target.absolute() != folder.absolute():
                    object_path = target.absolute().relative_to(folder.absolute())
                    stat = target.stat()
                    parent_object, _ = Object.objects.get_or_create(
                            folder=folder,
                            path=object_path,
                            defaults={
                                "is_dir": True,
                                "is_file": False,
                                "size": stat.st_size,
                                "update_datetime": timestamp2datetime(stat.st_ctime),
                            }
                    )
                self.scan(folder, target, kwargs["depth"], parent_object=parent_object)
            else:
                LOGGER.info("%s does not exist, skip scan", target)

    def scan(self, root_folder: RootFolder, scan_path: Path, remain_depth: int, parent_object=None):
        if remain_depth == 0:
            LOGGER.info("max depth reached, skip scan: %s", scan_path)
            return
        LOGGER.info("scan %s", scan_path)
        for path in scan_path.iterdir():
            path_str = to_unix_str(path.relative_to(root_folder.path))
            stat = path.stat()
            update_datetime = timestamp2datetime(stat.st_mtime)
            if path.is_dir():
                LOGGER.info("update %s with parent: %s", path, parent_object)
                next_parent_object, _ = Object.objects.update_or_create(
                        folder=root_folder,
                        path=path_str,
                        defaults={
                            "is_dir": True,
                            "is_file": False,
                            "size": stat.st_size,
                            "update_datetime": update_datetime,
                            "parent": parent_object,
                            "name": path.name,
                        }
                )
                LOGGER.info("next parent object: %s", next_parent_object)
                self.scan(
                        root_folder=root_folder,
                        scan_path=path,
                        remain_depth=remain_depth-1,
                        parent_object=next_parent_object
                )
                continue

            file_obj = Object.objects.filter(
                folder=root_folder,
                path=path_str,
            ).first()
            if file_obj is None:
                file_obj = Object.objects.create(
                    folder=root_folder,
                    path=path_str,
                    update_datetime=update_datetime,
                    size=stat.st_size,
                    parent=parent_object,
                    is_dir=True,
                    is_file=False,
                    name=path.name,
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
