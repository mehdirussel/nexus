from django.shortcuts import render,redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login,authenticate
from django.contrib.auth.views import LoginView
from .my_forms import NewUserForm

# Create your views here.
def create_user(request):
    if request.method == "POST":
        signup_form =  NewUserForm(request.POST,request.FILES)
        if signup_form.is_valid():
            user = signup_form.save()
            login(request, user)
            username = signup_form.cleaned_data.get("username")
            messages.success(request, f"Account Created for {username}")
            return redirect("login-view")
        else: # invalid signup_form
            messages.error(request, 'Please correct the errors below.')
    else:
        signup_form = NewUserForm()
    context = {'form':signup_form}
    return render(request, 'signup.html', context)


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST["username"],password=request.POST["password"])
        if user is not None:
            login(request, user)
            if "remember_me" not in request.POST.keys(): # remember is not checked, set the expiry to 0
                request.session.set_expiry(0)
            messages.success(request, 'Logged in successfully')
            return redirect('home-view') # redirect to channels:home-view
        else: # login failed
            messages.error(request, 'Log in Failed')
    return render(request, 'login.html')

