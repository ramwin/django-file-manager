from pathlib import Path

from django.db import models


class Folder(models.Model):
    path = models.FilePathField(unique=True)

    def __str__(self):
        return f"Folder: {self.path}"


class File(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    path = models.FilePathField("relative path to folder")
    md5 = models.CharField(max_length=32)
    size = models.IntegerField()
    update_datetime = models.DateTimeField()

    def __str__(self):
        return f"File: {self.folder}/{self.path}"

    def absolute(self):
        return Path(self.folder.path) / self.path  # pylint: disable=no-member
