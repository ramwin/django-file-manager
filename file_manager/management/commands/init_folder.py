#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from file_manager.models import RootFolder, Object


class Command(BaseCommand):

    help = "add a folder to managed folder"

    def add_arguments(self, parser):
        parser.add_argument("folders", nargs="+", type=str)

    def handle(self, *args, **kwargs):
        for folder_path in kwargs["folders"]:
            folder_path = Path(folder_path)
            assert folder_path.is_dir()
            folder, created = RootFolder.objects.get_or_create(
                path=folder_path.absolute())
            if created is False:
                self.stdout.write(
                    self.style.WARNING(f"{folder_path} already exists"))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"{folder} created"))
            Object.objects.get_or_create(
                folder=folder,
                path="./",
                is_file=False,
                is_dir=True,
                size=folder_path.stat().st_size,
                update_datetime=datetime.datetime.fromtimestamp(
                    folder_path.stat().st_mtime).astimezone(
                        timezone.get_default_timezone())
            )
