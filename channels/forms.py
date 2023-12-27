from django import forms
from channels.models import Channel

class NewChannelForm(forms.ModelForm):
    
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'new channel name'}),label='')
    class Meta:
        model = Channel
        fields = ['name']

