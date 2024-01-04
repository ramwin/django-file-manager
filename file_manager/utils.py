#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import datetime
import hashlib
import logging
from pathlib import Path
import random
import shutil

from django.utils import timezone


LOGGER = logging.getLogger(__name__)


def get_md5(path: Path) -> str:
    chunk_size = 4 * 1024 * 1024
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                return md5.hexdigest()
            md5.update(chunk)


def get_hash_path(root: Path, filehash: str, suffix="") -> Path:
    assert filehash
    directory = root / filehash[0:2]
    if directory.exists():
        return get_hash_path(directory, filehash[2:], suffix)
    return root / (filehash + suffix)


def optimize(folder: Path):
    """
    optmize the file in folder, limit it only contains max 256 file
    if it oversizes, i will sorte the filename and use the first two character as folder name.
    and move the file whose name start with this two character into it

    e.g.
        f
    """
    files = [
        f for f in folder.iterdir() if f.is_file()]
    if len(files) <= 256:
        return
    for file_path in files:
        sub_dir = folder.joinpath(file_path.stem[0:2])
        sub_dir.mkdir(exist_ok=True)
        target = sub_dir.joinpath(file_path.name[2:])
        if target.exists():
            raise FileExistsError("file exists", target)
        file_path.rename(target)


def backup(path: Path, root: Path, filehash: str):
    """
    copy a file to root, using the hash path
    """
    target = get_hash_path(root, filehash, path.suffix)
    if target.exists():
        error = f"file {target} exists, cannot backup {path}"
        LOGGER.error(error)
        raise FileExistsError(error)
    shutil.copy(path, target)
    if random.random() < 1/256:
        optimize(target.parent)


def timestamp2datetime(timestamp: float):
    return datetime.datetime.fromtimestamp(
        timestamp
    ).astimezone(
        timezone.get_default_timezone()
    )


def to_unix_str(path: Path):
    return str(path).replace("\\", "/")
