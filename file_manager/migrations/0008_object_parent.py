# Generated by Django 4.0.5 on 2023-05-21 00:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0007_object_is_dir_object_is_file_object_last_scan'),
    ]

    operations = [
        migrations.AddField(
            model_name='object',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='file_manager.object'),
        ),
    ]