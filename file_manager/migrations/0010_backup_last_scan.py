# Generated by Django 4.0.5 on 2023-05-21 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0009_alter_object_last_scan'),
    ]

    operations = [
        migrations.AddField(
            model_name='backup',
            name='last_scan',
            field=models.DateTimeField(null=True),
        ),
    ]
