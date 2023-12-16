from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required



# Create your views here.
@login_required(login_url='login-view')
def hello(request):
    return HttpResponse("hey there, channels speaking")