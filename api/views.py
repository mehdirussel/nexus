from rest_framework import generics, permissions, status
from rest_framework.response import Response
from channels.models import Channel, Message,perms_user_channel_rel,MessageReadStatus
from channels.views import is_user_in_channel
from .serializers import UserChannelsSerializer,ChannelDetailSerializer, MessageSerializer
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponse,JsonResponse,Http404
from django.contrib.auth.decorators import login_required



class UserChannelsAPIView(generics.ListAPIView):
    serializer_class = UserChannelsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return perms_user_channel_rel.objects.filter(user=user)

class ChannelMessagesAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        channel_id = self.kwargs['channel_id']
        return Message.objects.filter(channel__id=channel_id)

class ChannelDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ChannelDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    def get_queryset(self):
        user = self.request.user
        return Channel.objects.filter(members=user)


class MarkMessageAsReadAPIView(generics.UpdateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # verify if  user is a member of the channel
        channel_members = instance.channel.members.all()
        if request.user not in channel_members:
            return Response({"detail": "You do not have permission to mark this message as read."}, status=status.HTTP_403_FORBIDDEN)

        instance.is_read = True
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


@login_required(login_url='login-view')
def send_msg_api(request):
    
    if request.method == 'POST': # clicked on send button
        request_payload = json.loads(request.body.decode("utf-8"))
        try: 
            channel_id = request_payload['channel_id']
            content = request_payload['content']
        except KeyError:
            raise Http404("An error occured when sending the message!")
        
        c = get_object_or_404(Channel, id=channel_id)
        if not is_user_in_channel(request.user,c):
            raise Http404("You dont have access to this channel or it does not exist")
        
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)

        # all is good, we can add the message to channel
        
        m = Message(
            content=content,
            channel=c,
            user=request.user,
        )
        m.save()

        MessageReadStatus.objects.create( # user has read his message b4 sending it, unless its twitter
            user=request.user,
            message=m,
            is_read=True
        )

        for member in c.members.all(): # all other userss have not yet read the message
            if member != request.user:
                MessageReadStatus.objects.create(
                    user=member,
                    message=m,
                    is_read=False
                )

        return JsonResponse({'status': 'sent'}, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


