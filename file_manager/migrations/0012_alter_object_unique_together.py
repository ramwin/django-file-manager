# Generated by Django 4.0.5 on 2023-05-21 02:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0011_alter_backup_last_scan_alter_object_last_scan'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='object',
            unique_together={('folder', 'path')},
        ),
    ]