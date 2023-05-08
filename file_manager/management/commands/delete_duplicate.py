#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


# pylint:disable=unused-argument,missing-module-docstring,missing-function-docstring,missing-class-docstring,import-error,no-member


from pathlib import Path

from django.core.management.base import BaseCommand
from django.db.models import Count

from file_manager.models import File
from file_manager.utils import get_md5


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("-n", "--no-act", action="store_true", help="check before delete")

    def handle(self, *args, **kwargs):
        infos = list(
            File.objects.exclude(md5="").order_by(
                "md5"
            ).values("md5").annotate(count=Count("*")).filter(
                count__gte=2
            )
        )
        self.stdout.write(self.style.NOTICE("There files will be deleted:"))
        for info in infos:
            remove_file, keep_file = self.get_duplicate(info)
            self.stdout.write(self.style.ERROR(
                f"delete: {remove_file.absolute()}"))
            self.stdout.write(self.style.SUCCESS(
                f"keep: {keep_file.absolute()}"))
            if kwargs.get("no_act"):
                pass
            else:
                Path(remove_file.absolute()).unlink()
                remove_file.delete()

    @staticmethod
    def get_duplicate(info):
        queryset = File.objects.filter(
            md5=info["md5"],
        ).order_by("folder", "update_datetime")
        remove_file, keep_file = list(queryset[0:2])
        assert remove_file.absolute().exists()
        assert keep_file.absolute().exists()
        return remove_file, keep_file
