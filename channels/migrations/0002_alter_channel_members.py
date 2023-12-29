# Generated by Django 4.2.7 on 2023-12-26 22:40

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('channels', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='channels', through='channels.perms_user_channel_rel', to=settings.AUTH_USER_MODEL),
        ),
    ]