from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Channel,Message,perms_user_channel_rel
from django.contrib import messages
from .forms import NewChannelForm
from channels.models import Channel, perms_user_channel_rel
from django.core.exceptions import ValidationError


UserModel = get_user_model()


# Create your views here.
@login_required(login_url='login-view')
def home_view(request):
    user_channels_ids = [f"<a href='/channels/m/{c.id}'>{c.name}</a><br>" for c in request.user.channels.all()]

    return HttpResponse(f"hey there, here is the homepage, youre logged in as {request.user} <br>{user_channels_ids}")

@login_required(login_url='login-view')
def show_channel(request,slug):
    channel = get_object_or_404(Channel, id=slug)

    # Check if the user has access to the channel
    user_channel_rel = perms_user_channel_rel.objects.filter(user=request.user, channel=channel).first()
    if not user_channel_rel:
        return HttpResponseForbidden("You do not have access to this channel.")

    # get and sort messages for the channel by order of sending
    mesgs = Message.objects.filter(channel=channel).order_by('sent_at')
    s = ""
    i=1
    for m in mesgs:
        s += f'message {i}: {m.content} <br>'
        i+=1
    return HttpResponse(f"{s}")




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
