"""
admin config
"""

# pylint: disable=missing-class-docstring

from django.contrib import admin

from . import models


@admin.register(models.Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(models.RootFolder)
class RootFolderAdmin(admin.ModelAdmin):
    list_display = ["id", "bucket", "windows_path"]


@admin.register(models.Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ["id", "path", "size", "update_datetime", "folder"]
    list_filter = ["is_dir"]
    search_fields = ["path"]


@admin.register(models.Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ["id", "bucket", "path", "current_id", "current_update_datetime"]
