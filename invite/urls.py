from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url="/users/"),name="invite-home-view"),
    path('send/<channel_id>/<user_to_add>', views.send_invite_from_username_or_email,name="send-invite"), # add to send the invitation
    path("r/<invite_token>", views.validate_invite, name="validate-invite"), # r for reception, meaning need to validate the link
    path('send/<channel_id>', views.invite,name="invite"), # page for sendig invites 
]