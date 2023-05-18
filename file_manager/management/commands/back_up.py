#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


from django.core.management.base import BaseCommand
from file_manager.models import Backup


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for backup in Backup.objects.all():
            while True:
                result = backup.backup()
                if result is True:
                    break
