from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse,Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Channel,Message,perms_user_channel_rel,MessageReadStatus
from django.contrib import messages
from .forms import NewChannelForm


UserModel = get_user_model()

def is_user_in_channel(user, channel):
    try:
        perms_user_channel_rel.objects.get(user=user, channel=channel)
        return True
    except perms_user_channel_rel.DoesNotExist:
        return False

# Create your views here.
@login_required(login_url='login-view')
def home_view(request):
    
    #return HttpResponse(f"hey there, here is the homepage, youre logged in as {request.user} <br>{user_channels_ids} {s}")
    channel_list = request.user.channels.all()

    # for private channels, change the name to other user username
    for c in channel_list:
        if c.is_private: 
            for m in c.members.all():
                if request.user.username != m.username: # found the other user
                    c.name = m.username
                    break

    return render(request, 'homepage.html', {'channel_list': channel_list})

@login_required(login_url='login-view')
def show_channel(request,slug):
    channel = get_object_or_404(Channel, id=slug)

    # Check if the user has access to the channel
    user_channel_rel = perms_user_channel_rel.objects.filter(user=request.user, channel=channel).first()
    if not user_channel_rel:
        return HttpResponseForbidden("You do not have access to this channel.")

    # get and sort messages for the channel by order of sending
    mesgs = Message.objects.filter(channel=channel).order_by('sent_at')

    # for private channels, change the name to other user username
    if channel.is_private: 
            for m in channel.members.all():
                if request.user.username != m.username: # found the other user
                    channel.name = m.username
                    break

    return render(request, 'channel_template.html', {'channel': channel,"msg_list":mesgs})




@login_required(login_url='login-view')
def new_channel(request):
    if request.method == "POST":
        channel_form = NewChannelForm(request.POST)
        if channel_form.is_valid():
            
            # Create a new channel
            new_channel = channel_form.save(commit=False)
            new_channel.creator_user = request.user
            new_channel.participants += 1
            new_channel.save()

            # Add the creator as a moderator to the channel
            perms_user_channel_rel.objects.create(user=request.user, channel=new_channel, is_moderator=True)

            messages.success(request, f"Channel '{new_channel.name}' created successfully.")
            return redirect(f'/channels/m/{new_channel.id}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        channel_form = NewChannelForm()

    context = {'form': channel_form}
    return render(request, 'create_channel.html', context)

def options_channel(request,slug):
    channel = get_object_or_404(Channel, id=slug)
    if channel.is_private:
        raise Http404("You can't change this channel")
    return render(request, 'channel_options.html',{'channel': channel})

def delete_channel(request,slug):
    channel = get_object_or_404(Channel, id=slug)
    if request.method == 'POST':
        # Supprimer le compte de l'utilisateur actuel
        channel.delete()
        # Déconnecter l'utilisateur après suppression
        return redirect('home-view')  # Rediriger vers la page d'accueil ou une autre vue
    return render(request, 'channel_delete.html',{'channel': channel})

def modify_channel(request, slug):
    channel = get_object_or_404(Channel, id=slug)

    if request.method == 'POST':
        form = NewChannelForm(request.POST, instance=channel)
        if form.is_valid():
            form.save()
            return redirect('options-channel', slug=channel.id)  # Redirigez vers la page d'options du canal modifié
    else:
        form = NewChannelForm(instance=channel)

    return render(request, 'channel_modify.html', {'form': form, 'channel': channel})