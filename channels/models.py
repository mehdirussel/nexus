from django.db import models
from django.contrib.auth import get_user_model
from uuid import uuid4

UserModel = get_user_model()
# Create your models here.

class Channel(models.Model):
    # canaux de discussion
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(to=UserModel, through='perms_user_channel_rel', related_name='channels',blank=True)
    creator_user = models.ForeignKey(to=UserModel,related_name='created_channels', on_delete=models.CASCADE)
    participants = models.IntegerField(default=0)
    is_private = models.BooleanField(default=False)
    

    def __str__(self):
        return self.name


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    content = models.TextField()
    channel = models.ForeignKey(to=Channel, on_delete=models.CASCADE, related_name='channel_messages')
    user = models.ForeignKey(to=UserModel, on_delete=models.CASCADE, related_name='user_messages')
    sent_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Message from {self.user.username} in {self.channel.name} : {self.content} | sent at: {self.sent_at}"

class perms_user_channel_rel(models.Model): # relationship between user and channel to know the user's perms
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    # permissions here
    is_moderator = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} is {'' if self.is_moderator else 'not'} a mod of {self.channel.name}"

class MessageReadStatus(models.Model):# relationship between user and message to know if a message is read by a user or not
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} has{'' if self.is_read else 'nt'} read the message"