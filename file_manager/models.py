# pylint: disable=no-member

import logging
from pathlib import Path
import shutil

from django.db import models
from django.utils import timezone

from hashfs import HashFS

from .utils import get_md5, timestamp2datetime


LOGGER = logging.getLogger(__name__)


class Bucket(models.Model):
    """
    a bucket contains several folders
    """
    name = models.CharField(unique=True, max_length=31)

    def __str__(self):
        return f"{self.id}: {self.name}"


class RootFolder(models.Model):
    bucket = models.ForeignKey(
        Bucket, null=True, on_delete=models.DO_NOTHING)
    path = models.FilePathField(unique=True)

    def __str__(self):
        return f"RootFolder: {self.path}"

    def absolute(self):
        return Path(self.path)


class Object(models.Model):
    """
    the Object works like a tree. every folder should contains a object whose parent is None
    """
    folder = models.ForeignKey(RootFolder, on_delete=models.CASCADE)
    path = models.FilePathField("relative path to folder")
    md5 = models.CharField(max_length=32, db_index=True)
    size = models.IntegerField(db_index=True)
    update_datetime = models.DateTimeField()
    is_file = models.BooleanField(default=True)
    is_dir = models.BooleanField(default=False)
    last_scan = models.DateTimeField(null=True, db_index=True)
    parent = models.ForeignKey("self", null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f"Object: {self.folder}/{self.path}"

    @classmethod
    def get_or_create_from_path(cls, folder, path: Path):
        rel_path = path.relative_to(folder.absolute())
        LOGGER.info("create path: %s, rel_path: %s", path, rel_path)
        if rel_path == Path("."):
            parent = None
        else:
            parent = cls.get_or_create_from_path(
                folder=folder,
                path=path.parent,
            )
        try:
            return cls.objects.get(
                folder=folder,
                path=rel_path,
            )
        except cls.DoesNotExist:
            info = path.stat()
            return cls.objects.create(
                folder=folder,
                path=rel_path,
                size=info.st_size,
                update_datetime=timestamp2datetime(info.st_mtime),
                is_file=False,
                is_dir=True,
                parent=parent,
            )

    def scan(self):
        LOGGER.info("re scan: %s", self.absolute())
        now = timezone.now()
        path = self.absolute()
        if self.is_file:
            if self.size != path.stat().st_size or self.update_datetime != timestamp2datetime(path.stat().st_mtime):
                self.update_md5()
        if self.is_dir:
            for child in path.iterdir():
                rel_path = child.relative_to(self.folder.absolute())
                try:
                    Object.objects.get(
                        folder=self.folder,
                        path=rel_path,
                    )
                except Object.DoesNotExist:
                    Object.objects.create(
                        folder=self.folder,
                        path=rel_path,
                        parent=self,
                        size=child.stat().st_size,
                        update_datetime=timestamp2datetime(
                           child.stat().st_mtime),
                        is_file=child.is_file(),
                        is_dir=child.is_dir(),
                    )
            if self.parent is None and (self.path != "."):
                self.parent = self.get_or_create_from_path(
                    folder=self.folder,
                    path=self.absolute().parent,
                )
        self.last_scan = now
        self.save()

    def absolute(self):
        return Path(self.folder.path) / self.path  # pylint: disable=no-member

    def update_md5(self):
        assert not self.md5
        self.md5 = get_md5(self.absolute())
        self.save()

    class Meta:
        unique_together = (("folder", "path"), )


class Backup(models.Model):
    bucket = models.ForeignKey(
        Bucket, on_delete=models.DO_NOTHING)
    path = models.FilePathField(unique=True)
    current_id = models.IntegerField("Bigest synced id", default=0)
    current_update_datetime = models.DateTimeField("newest updated datetime", null=True)
    cnt = models.IntegerField(default=0)
    last_scan = models.DateTimeField(null=True, db_index=True)

    def filter_un_backuped_files(self):
        """
        currently, only filter by id. so the Object should never change
        """
        bucket_file_qs = Object.objects.filter(  # pylint: disable=no-member
            folder__bucket=self.bucket,
            id__gt=self.current_id,
        )
        return bucket_file_qs.order_by("id")

    def backup_db(self):
        target = Path(
            self.absolute(),
            ".dbfiles",
            timezone.now().strftime("%Y-%m-%d %H-%M-%S-%f") + ".db"
        )
        LOGGER.info("backup db to: %s", target)
        target.parent.mkdir(exist_ok=True,
                            parents=True)
        assert not target.exists(), target
        shutil.copy("db.sqlite3", target)

    def backup(self, max_size=1024) -> bool:
        """
        backup max max_size files.
        if all Object in the self.bucket is backuped, return True
        """
        queryset = self.filter_un_backuped_files()
        remain = queryset.count()
        LOGGER.info("backup %d/%s files", max_size, remain)
        for file_obj in queryset[0:max_size]:
            self.sync_file(file_obj)
        self.backup_db()
        if remain <= max_size:
            self.last_scan = timezone.now()
            self.save()
            return True
        return False

    def sync_file(self, file_obj):
        if not file_obj.md5:
            file_obj.update_md5()
        hashfs = HashFS(root=self.absolute(), algorithm="md5")
        hashfs.put_file(file_obj.absolute(), hashid=file_obj.md5)
        self.current_id = file_obj.id
        self.cnt += 1
        self.save()

    def absolute(self):
        return Path(self.path).absolute()

    def __str__(self):
        return f"{self.id}: {self.bucket} back to {self.path}"
