from rest_framework import serializers
from channels.models import Channel, Message,perms_user_channel_rel, MessageReadStatus
from users.models import NexusUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NexusUser 
        fields = ['username', 'photo_de_profil']

class UserChannelsSerializer(serializers.ModelSerializer): # to get list of channels of certain user
    class Meta:
        model = perms_user_channel_rel
        fields = '__all__'

    
class MessageSerializer(serializers.ModelSerializer):# to get messages
    user = UserSerializer()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'content', 'user', 'is_read', 'sent_at','channel']

    def get_is_read(self, obj):
        request_user = self.context['request'].user
        try:
            read_status = MessageReadStatus.objects.get(user=request_user, message=obj)
            return read_status.is_read
        except MessageReadStatus.DoesNotExist:
            return False


class ChannelDetailSerializer(serializers.ModelSerializer): # to get details on channels
    class Meta:
        model = Channel
        fields = '__all__'
