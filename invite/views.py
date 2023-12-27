from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from channels.models import Message,Channel
from django.core.signing import TimestampSigner,BadSignature,SignatureExpired
from django.contrib import messages
from django.urls import reverse
from base64 import urlsafe_b64decode,urlsafe_b64encode
from django.shortcuts import get_object_or_404
from channels.models import perms_user_channel_rel
from django.http import Http404


UserModel = get_user_model()
invitation_expiry_delay = 1#24*3600 # 1 day in seconds

def is_user_in_channel(user, channel):
    try:
        perms_user_channel_rel.objects.get(user=user, channel=channel)
        return True
    except perms_user_channel_rel.DoesNotExist:
        return False

@login_required(login_url='login-view')
def validate_invite(request,invite_token):

    try: # link and data valid
        decoded_data = TimestampSigner().unsign_object(urlsafe_b64decode(invite_token).decode(),max_age=invitation_expiry_delay)
        channel_id = decoded_data["channel_id"]
        channel = get_object_or_404(Channel, id=channel_id)
        if request.user in channel.members.all(): # user already exists in channel
            messages.error(request, f"You are already a member of {channel.name}.")
        else: # user not rpesent
            #channel.members.add(request.user)
            channel.participants = channel.participants + 1
            perms_user_channel_rel.objects.create(user=request.user, channel=channel, is_moderator=False)
            messages.success(request, f"{request.user.username} has been added to {channel.name}.")
        
    except SignatureExpired: # invitation link is expired
        messages.error(request, 'This invitation link is expired,ask for a new one')
    except Exception:
        messages.error(request, 'Invalid invitation link')
    
    return redirect("home-view")
    #return render(request, 'homepage.html')



def gen_invite_link(channel_id): # generates a link to invite other users to a channel
    # will generate a timestamped and urlsafe base64 encoded token that contains the channel_id
    # every logged user who clicks the link is added to the channel if not already
    
    timestamped_token = TimestampSigner().sign_object({"channel_id":channel_id})
    b64_token = urlsafe_b64encode(timestamped_token.encode()).decode()
    return b64_token
    

@login_required(login_url='login-view')
def send_invite_from_username_or_email(request, user_to_add,channel_id):

    c = get_object_or_404(Channel, id=channel_id)
    if c.is_private:
        #messages.error(request, "This is a private chat, it cannot be shared")
        #return HttpResponse("This is a private chat, it cannot be shared")
        raise Http404("This is a private chat, it cannot be shared")
    if not is_user_in_channel(request.user,c):
        raise Http404("You dont have access to this channel or it does not exist")
    
    token = gen_invite_link(channel_id)

    try: # found through email
        user = UserModel.objects.get(email__exact=user_to_add)
    except UserModel.DoesNotExist:
        try:  # found through username
            user = UserModel.objects.get(username=user_to_add)
        except UserModel.DoesNotExist: # didnt fund iser
            messages.error(request, "This user does not exist!!!!")
            return

    invite_message = f"{request.user.username} has invited you to join his chatroom {c.name}: click on this link to join {request.build_absolute_uri(reverse('validate-invite', kwargs={'invite_token': token}))}"
    print(invite_message)
    
    # get the channel of direct messages between the 2 and send the message
    channel = Channel.objects.filter(members=request.user).filter(members=user, participants=2)[0]
    
    m = Message(
        content = invite_message,
        channel = channel,
        user = request.user
    )
    m.save()
    return redirect('/channels/m/'+channel_id)



