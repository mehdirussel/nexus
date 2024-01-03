from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordChangeForm
from .models import NexusUser

class NewUserForm(UserCreationForm): 
    # UserCreationForm doesnt allow case-equivalent usernames,
    #  eg: amontarad and aMoNTArad are considered the same
	username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'username'}),label='')
	email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder':'email uha'}),label='')
	photo_de_profil = forms.ImageField(widget=forms.FileInput(attrs={"style":"padding-top: 11px;"}),label='')
	password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}),label='')
	password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password'}),label='')
	class Meta:
		model = NexusUser
		fields = ("username", "email", "password1","password2","photo_de_profil")
	
		
class Password_change_form(PasswordChangeForm):
	pass

class LoginForm(AuthenticationForm):
	pass

class EditUserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'username'}), label='')
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'email uha'}), label='')
    photo_de_profil = forms.ImageField(widget=forms.FileInput(attrs={"style": "padding-top: 11px;"}), label='')

    class Meta:
        model = NexusUser
        fields = ("username", "email", "photo_de_profil")

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = True  # Empêche la modification du nom d'utilisateur

    def clean_email(self):
        email = self.cleaned_data['email']
        existing_user = NexusUser.objects.exclude(pk=self.instance.pk).filter(email=email)
        if existing_user.exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé par un autre utilisateur.")
        return email