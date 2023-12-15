from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import NexusUser
class NewUserForm(UserCreationForm): 
    # UserCreationForm doesnt allow case-equivalent usernames,
    #  eg: amontarad and aMoNTArad are considered the same

	class Meta:
		model = NexusUser
		fields = ("username", "email", "password1","photo_de_profil")