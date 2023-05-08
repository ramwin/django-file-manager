#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


from pathlib import Path

from django.core.management.base import BaseCommand

from file_manager.models import Folder


class Command(BaseCommand):

    help = "add a folder to managed folder"

    def add_arguments(self, parser):
        parser.add_argument("folders", nargs="+", type=str)

    def handle(self, *args, **kwargs):
        for folder_path in kwargs["folders"]:
            folder_path = Path(folder_path)
            folder, created = Folder.objects.get_or_create(
                path=folder_path.absolute())
            if created is False:
                self.stdout.write(
                    self.style.WARNING(f"{folder_path} already exists"))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"{folder} created"))
