from django.contrib import admin
from .models import perms_user_channel_rel, Channel, Message,MessageReadStatus
# Register your models here.

admin.site.register(perms_user_channel_rel)
admin.site.register(Channel)
admin.site.register(Message)
admin.site.register(MessageReadStatus)
