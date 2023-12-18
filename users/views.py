from django.shortcuts import render,redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login,authenticate
from django.contrib.auth.views import LoginView
from .my_forms import NewUserForm
from django.core.signing import TimestampSigner
from base64 import urlsafe_b64encode

def gen_email_token(email):
    timestamp_token = TimestampSigner().sign_object({"email":email})
    email_verif_token = urlsafe_b64encode(timestamp_token.encode()).decode()
    
    return email_verif_token

def send_email(r,email):
    #messages.success(r,r.build_absolute_uri(reverse("nexus-hello-view")) + gen_email_token(email))
    return r.build_absolute_uri(reverse("empty-verify-view")) + gen_email_token(email)

# Create your views here.
def create_user(request):
    if request.method == "POST":
        signup_form =  NewUserForm(request.POST,request.FILES)
        if signup_form.is_valid():
            user = signup_form.save()
            user.is_active = False # compte désactivé jusqu'a verification de mail
            user.save()
            
            # email verification stuff
            messages.success(request, send_email(request,signup_form.cleaned_data.get("email")))

            username = signup_form.cleaned_data.get("username")
            messages.success(request, f"Account created for {username}. Please follow the instructions received by email to confirm your account.")
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
        if user is not None: # email vérifié
            if user.is_active:
                login(request, user)
                if "remember_me" not in request.POST.keys(): # remember is not checked, set the expiry to 0
                    request.session.set_expiry(0)
                messages.success(request, 'Logged in successfully')
                return redirect('home-view') # redirect to channels:home-view
            else: # email pas encore vérifié
                
                messages.error(request, 'Your account is not verified! To access the app, please check your email for a verification link.')
        else: # login failed
            messages.error(request, 'Login failed! Please check your credentials and try again.')
    return render(request, 'login.html')


