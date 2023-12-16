from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import NexusUser

class NewUserForm(UserCreationForm): 
    # UserCreationForm doesnt allow case-equivalent usernames,
    #  eg: amontarad and aMoNTArad are considered the same
	username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'username'}),label='')
	email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder':'email uha'}),label='')
	photo_de_profil = forms.ImageField(widget=forms.FileInput(attrs={'placeholder':'image'}),label='')
	password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}),label='')
	password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password'}),label='')
	class Meta:
		model = NexusUser
		fields = ("username", "email", "password1","password2","photo_de_profil")


class LoginForm(AuthenticationForm):
	pass