import logging
from pathlib import Path
import shutil

from django.db import models
from django.utils import timezone
from .utils import backup, get_md5


LOGGER = logging.getLogger(__name__)


class Bucket(models.Model):
    """
    a bucket contains several folders
    """
    name = models.CharField(unique=True, max_length=31)


class Folder(models.Model):
    bucket = models.ForeignKey(
        Bucket, null=True, on_delete=models.DO_NOTHING)
    path = models.FilePathField(unique=True)

    def __str__(self):
        return f"Folder: {self.path}"


class File(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    path = models.FilePathField("relative path to folder")
    md5 = models.CharField(max_length=32, db_index=True)
    size = models.IntegerField(db_index=True)
    update_datetime = models.DateTimeField()

    def __str__(self):
        return f"File: {self.folder}/{self.path}"

    def absolute(self):
        return Path(self.folder.path) / self.path  # pylint: disable=no-member

    def update_md5(self):
        assert not self.md5
        self.md5 = get_md5(self.absolute())
        self.save()


class Backup(models.Model):
    bucket = models.ForeignKey(
        Bucket, on_delete=models.DO_NOTHING)
    path = models.FilePathField(unique=True)
    current_id = models.IntegerField("Bigest synced id", default=0)
    current_update_datetime = models.DateTimeField("newest updated datetime", null=True)
    cnt = models.IntegerField(default=0)

    def filter_un_backuped_files(self):
        """
        currently, only filter by id. so the file should never change
        """
        bucket_file_qs = File.objects.filter(  # pylint: disable=no-member
            folder__bucket=self.bucket,
            id__gt=self.current_id,
        )
        return bucket_file_qs.order_by("id")

    def backup_db(self):
        target = Path(
            self.absolute(),
            ".dbfiles",
            timezone.now().strftime("%Y-%m-%d %H-%M-%S") + ".db"
        )
        LOGGER.info("backup db to: %s", target)
        target.parent.mkdir(exist_ok=True,
                            parents=True)
        assert not target.exists(), target
        shutil.copy("db.sqlite3", target)

    def backup(self, max_size=1024) -> bool:
        """
        backup max max_size files.
        if all file in the self.bucket is backuped, return True
        """
        queryset = self.filter_un_backuped_files()
        if not queryset.exists():
            return True
        LOGGER.info("backup %d/%s files", max_size, queryset.count())
        for file_obj in queryset[0:max_size]:
            self.sync_file(file_obj)
        self.backup_db()
        return False

    def sync_file(self, file_obj):
        if not file_obj.md5:
            file_obj.update_md5()
        backup(file_obj.absolute(), self.absolute(),
               filehash=file_obj.md5)
        self.current_id = file_obj.id
        self.cnt += 1
        self.save()

    def absolute(self):
        return Path(self.path).absolute()
