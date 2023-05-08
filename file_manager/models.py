from django.db import models

# Create your models here.


class Folder(models.Model):
    path = models.FilePathField()


class File(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    path = models.FilePathField()
    md5 = models.CharField(max_length=32)
