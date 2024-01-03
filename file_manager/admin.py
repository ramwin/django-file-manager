"""
admin config
"""

# pylint: disable=missing-class-docstring

from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from . import models


@admin.register(models.Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(models.RootFolder)
class RootFolderAdmin(admin.ModelAdmin):
    list_display = ["id", "bucket", "windows_path", "linux_path"]


@admin.register(models.Object)
class ObjectAdmin(MPTTModelAdmin):
    list_display = ["id", "path", "size", "update_datetime", "folder"]
    list_filter = ["is_dir", "folder__bucket", "folder"]
    readonly_fields = ["last_scan", "parent"]
    search_fields = ["path"]
    mptt_level_indent = 4


@admin.register(models.Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ["id", "bucket", "path", "current_id", "current_update_datetime"]
