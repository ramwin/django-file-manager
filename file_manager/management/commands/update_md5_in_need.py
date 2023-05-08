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

    def handle(self, *args, **kwargs):
        queryset = File.objects.order_by(
            "size").values(
                'size').annotate(count=Count("*")).filter(
                    count__gte=2)
        for info in queryset:
            for f in File.objects.filter(md5="",
                                         size=info['size']):
                self.stdout.write(self.style.HTTP_INFO(f"cal the md5 of {f}"))
                md5 = get_md5(Path(f.folder.path) / f.path)
                f.md5 = md5
                f.save()
