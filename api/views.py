from rest_framework import generics, permissions, status
from rest_framework.response import Response
from channels.models import Channel, Message,perms_user_channel_rel,MessageReadStatus
from channels.views import is_user_in_channel
from .serializers import UserChannelsSerializer,ChannelDetailSerializer, MessageSerializer
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponse,JsonResponse,Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages



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
        channel = Channel.objects.filter(id=channel_id, members=self.request.user).first()
        if not is_user_in_channel(self.request.user,channel):
            raise Http404("You dont have access to this channel or it does not exist")
        
        return Message.objects.filter(channel__id=channel_id)


class ChannelDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ChannelDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    def get_queryset(self):
        user = self.request.user
        return Channel.objects.filter(members=user)

class ChannelUnreadMessagesAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        channel_id = self.kwargs['channel_id']
        user = self.request.user
        channel = Channel.objects.filter(id=channel_id).first()
        if not is_user_in_channel(user,channel):
            raise Http404("You dont have access to this channel or it does not exist")
        

        
        unread_messages_in_all_channels = MessageReadStatus.objects.filter(
            user=user,
            is_read=False
        )
        
        # filter those unread messages by channel id
        unread_messages = Message.objects.filter(
            messagereadstatus__in=unread_messages_in_all_channels,
            channel__id = channel_id
        )

        #print(f"{user.username} tried to get new messages: {[m.content for m in unread_messages]}")
        return unread_messages


@login_required(login_url='login-view')
def mark_message_read_api(request,message_id):

    if request.method == 'GET': # clicked on send button
        try:
            # check if message exists and is not read and is associated to the user
            instance = Message.objects.get(id=message_id)
            read_status = MessageReadStatus.objects.get(user=request.user,message=instance)
            
        except Message.DoesNotExist:
            return JsonResponse({'status': 'Message not found','message_id':message_id}, status=404)
        
        except MessageReadStatus.DoesNotExist:
            return JsonResponse({'status': 'Message status object not found','message_id':message_id}, status=404)
        

        read_status.is_read = True
        read_status.save()
        print(f"{request.user.username} marked the message {instance.id} as read")
        return JsonResponse({'status': 'marked as read','message_id':message_id}, status=200)

    else:
        return JsonResponse({'status': 'error, only get requests supported'}, status=405)

@login_required(login_url='login-view')
def delete_msg(request,message_id):
    if request.method == 'GET': # clicked on send button
        try:
            message = Message.objects.get(id=message_id)
            channel = message.channel
            # check if user is mod in this channel
            if perms_user_channel_rel.objects.filter(user=request.user, channel=channel, is_moderator=True).exists():
                # user is a mod and can delete the message
                message.delete()
                #messages.success(request,"message supprimé")
                return JsonResponse({'status': 'message deleted','message_id':message_id}, status=200)
            else: # not allowed
                return JsonResponse({'status': 'grr,not allowed'}, status=404)
            
            
        except Message.DoesNotExist:
            return JsonResponse({'status': 'Message not found','message_id':message_id}, status=404)
        
        except perms_user_channel_rel.DoesNotExist:
            return JsonResponse({'status': 'Message status object not found','message_id':message_id}, status=404)
            

            

    else:
        return JsonResponse({'status': 'error, only get requests supported'}, status=405)

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
        
        #print("message content: ",content)
        m = Message(
            content=content,
            channel=c,
            user=request.user,
        )
        m.save()


        for member in c.members.all(): # all userss have not yet read the message
            MessageReadStatus.objects.create(
                    user=member,
                    message=m,
                    is_read=False
                )
            print(f"created status for {member.username}")

        return JsonResponse({'status': 'sent'}, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


