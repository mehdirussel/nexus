from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from channels.models import Message,Channel,MessageReadStatus,perms_user_channel_rel
from django.core.signing import TimestampSigner,BadSignature,SignatureExpired
from django.contrib import messages
from django.urls import reverse
from base64 import urlsafe_b64decode,urlsafe_b64encode
from django.shortcuts import get_object_or_404
from django.http import Http404,HttpResponseNotFound
from users.models import NexusUser

UserModel = get_user_model()
invitation_expiry_delay = 24*3600 # 1 day in seconds

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
            messages.error(request, f"Vous êtes déjà membre de {channel.name}.")
        else: # user not rpesent
            #channel.members.add(request.user)
            channel.participants = channel.participants + 1
            channel.save()
            perms_user_channel_rel.objects.create(user=request.user, channel=channel, is_moderator=False)
            messages.success(request, f"{request.user.username} a rejoint {channel.name}.")
        
    except SignatureExpired: # invitation link is expired
        messages.error(request, "Ce lien d'invitation est expiré. veuillez demander un autre")
    except Exception:
        messages.error(request, "Lien d'invitation invalide")
    
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
        return HttpResponseNotFound(request,"Vous ne pouvez pas inviter des membres aux discussions privées.")
    if not is_user_in_channel(request.user,c):
        #messages.error(request, "You dont have access to this channel or it does not exist")
        return HttpResponseNotFound(request,"Vous n'avez pas accès à ce salon ou il n'existe pas.")
    
    token = gen_invite_link(channel_id)

    try: # found through email
        user = UserModel.objects.get(email__exact=user_to_add)
    except UserModel.DoesNotExist:
        try:  # found through username
            user = UserModel.objects.get(username=user_to_add)
        except UserModel.DoesNotExist: # didnt fund iser
            #messages.error(request, "This user does not exist!!!!")
            return HttpResponseNotFound(request,"Cet utilisateur n'existe pas.")
    
    if is_user_in_channel(user,c): # user_to_add already exists in the chnnel, no need to send an invite
        return HttpResponseNotFound(request, "Cet utilisateur est déjà membre du salon.")

    invite_message = f"{request.user.username} vous a invité au salon {c.name}, veuillez clicker sur ce lien pour le rejoindre: {request.build_absolute_uri(reverse('validate-invite', kwargs={'invite_token': token}))}"
    
    
    # get the channel of direct messages between the 2 and send the message
    
    channel = Channel.objects.filter(members=request.user).filter(members=user, participants=2).first()
    if channel is None:
        return HttpResponseNotFound(request, "a private channel between the 2 users doesnt exist for some reason! ")

    
    m = Message(
        content = invite_message,
        channel = channel,
        user = request.user
    )
    m.save()
    MessageReadStatus.objects.create( # user should read his message b4 sending it
            user=request.user,
            message=m,
            is_read=True
        )

    for member in channel.members.all(): # all other userss have not yet read the message
        if member != request.user:
            MessageReadStatus.objects.create(
                user=member,
                message=m,
                is_read=False
        )
    
    return HttpResponse(request,f"Invitation envoyée à {user_to_add}")



def invite(request,channel_id):
    channel = get_object_or_404(Channel, id=channel_id)
    
    if request.method == 'POST':
        username = request.POST.get('username')

        # Vérifiez si l'utilisateur avec le nom d'utilisateur donné existe
        try:
            user = NexusUser.objects.get(username=username)
        except NexusUser.DoesNotExist:
            # Gérer le cas où l'utilisateur n'existe pas
            return render(request, 'invite.html', {'channel': channel, 'error_message': 'Utilisateur non trouvé'})

        # Redirigez vers le chemin 'send-invite' avec l'ID de l'utilisateur
        return redirect(reverse('send-invite', kwargs={'channel_id': channel_id, 'user_to_add': user.id}))

    return render(request, 'send_invite.html', {'channel': channel})