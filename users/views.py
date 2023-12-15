from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import NewUserForm

# Create your views here.
def create_user(request):
    if request.method == "POST":
        form =  NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            username = form.cleaned_data.get("username")
            messages.success(request, f"Account Created for {username}")
            return redirect("home")
        else: # invalid form
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NewUserForm()
    context = {'form':form}  
    return render(request, 'signup.html', context)


        