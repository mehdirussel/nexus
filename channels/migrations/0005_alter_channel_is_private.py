# Generated by Django 4.2.7 on 2023-12-27 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0004_channel_is_private'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
    ]
