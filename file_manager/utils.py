#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import hashlib
from pathlib import Path


def get_md5(path: Path) -> str:
    CHUNK_SIZE = 4 * 1024 * 1024
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                return md5.hexdigest()
            md5.update(chunk)
