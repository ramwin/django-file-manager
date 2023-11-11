#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging
from django_commands import AutoLogCommand

from file_manager


LOGGER = logging.getLogger(__name__)


class Command(AutoLogCommand):

    def add_arguments(self, parser):
        parser.add_argument("-n", "--no-act", action="store_true", help="check before delete")

    def handle(self, *args, **kwargs):
        act = not kwargs.get("no_act")
