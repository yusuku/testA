# Generated by Django 4.1.5 on 2023-01-24 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("modeluse", "0009_remove_objfile_url_objfile_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="file",
            field=models.FileField(default=1, upload_to=""),
            preserve_default=False,
        ),
    ]
