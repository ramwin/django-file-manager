# Generated by Django 4.0.5 on 2023-05-08 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='md5',
            field=models.CharField(db_index=True, max_length=32),
        ),
        migrations.AlterField(
            model_name='file',
            name='size',
            field=models.IntegerField(db_index=True),
        ),
    ]
