from rest_framework import serializers
from channels.models import perms_user_channel_rel

class UserChannelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = perms_user_channel_rel
        fields = '__all__'
