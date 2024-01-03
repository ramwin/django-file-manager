#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging
from pathlib import Path

from file_manager.models import Object


LOGGER = logging.getLogger(__name__)


def run():
    for i in Object.objects.filter(name=None)[0:1000]:
        if '\\' in i.path:
            i.path = i.path.replace("\\", "/")
            linux_object =  Object.objects.filter(path=i.path, folder=i.folder).first()
            if linux_object:
                LOGGER.info("exist linux path %s, delete windows path %s",
                            linux_object, i)
                i.delete()
                continue
        i.name = Path(i.path).name
        LOGGER.info("save name %s %s", i, i.name)
        i.save()
    LOGGER.info("remain objects with no name: %d", Object.objects.filter(name=None).count())
