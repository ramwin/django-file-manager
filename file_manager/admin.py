"""
admin config
"""

# pylint: disable=missing-class-docstring

import logging

from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from . import models


LOGGER = logging.getLogger(__name__)


@admin.register(models.Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(models.RootFolder)
class RootFolderAdmin(admin.ModelAdmin):
    list_display = ["id", "bucket", "windows_path", "linux_path"]


@admin.action(description="clean backup file")
def clean_backup_file(modeladmin, request, queryset):
    for obj in queryset:
        LOGGER.info("delete backup of %s", obj)
        obj.rm_backup()


@admin.register(models.Object)
class ObjectAdmin(MPTTModelAdmin):
    list_display = ["id", "name", "parent", "is_dir", "is_file", "size", "update_datetime", "md5", "folder"]
    list_filter = ["is_dir", "folder__bucket", "folder"]
    readonly_fields = ["last_scan", "parent", "folder", "name", "md5", "size", "update_datetime", "is_file", "is_dir", "path"]
    search_fields = ["path"]
    mptt_level_indent = 4
    actions = [clean_backup_file]


@admin.register(models.Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ["id", "bucket", "path", "current_id", "current_update_datetime"]
