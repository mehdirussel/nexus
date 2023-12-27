from rest_framework import generics, permissions
from channels.models import perms_user_channel_rel
from .serializers import UserChannelsSerializer

class UserChannelsAPIView(generics.ListAPIView):
    serializer_class = UserChannelsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return perms_user_channel_rel.objects.filter(user=user)