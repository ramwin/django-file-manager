# Generated by Django 4.0.5 on 2023-05-14 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('file_manager', '0002_alter_file_md5_alter_file_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bucket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=31, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='folder',
            name='bucket',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='file_manager.bucket'),
        ),
    ]
