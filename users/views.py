from django.shortcuts import render,redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login,authenticate
from django.contrib.auth.views import LoginView
from .my_forms import NewUserForm,Password_change_form 
from .models import NexusUser
from channels.models import Channel,perms_user_channel_rel
from django.core.signing import TimestampSigner,BadSignature,SignatureExpired
from base64 import urlsafe_b64encode,urlsafe_b64decode


password_reset_delay = 10*60 # 10 minutes (in seconds)


def gen_email_token(email):
    timestamp_token = TimestampSigner().sign_object({"email":email})
    email_verif_token = urlsafe_b64encode(timestamp_token.encode()).decode()
    
    return email_verif_token

def send_email(r,email):
    #messages.success(r,r.build_absolute_uri(reverse("nexus-hello-view")) + gen_email_token(email))
    return r.build_absolute_uri(reverse("empty-verify-view")) + gen_email_token(email)

# Create your views here.
def create_user(request):
    if request.user.is_authenticated:
        return redirect('home-view')
    if request.method == "POST":
        signup_form =  NewUserForm(request.POST,request.FILES)
        if signup_form.is_valid():
            user = signup_form.save()
            user.is_active = False # compte désactivé jusqu'a verification de mail
            
            
            # create a channel between the new user and all existing users
            existing_users = NexusUser.objects.exclude(id=user.id).exclude(is_superuser=True)
            for existing_user in existing_users:
                channel = Channel.objects.create(name=f"{user.username}_{existing_user.username}", creator_user=user, participants=2,is_private=1)
                perms_user_channel_rel.objects.create(user=user, channel=channel, is_moderator=False)
                perms_user_channel_rel.objects.create(user=existing_user, channel=channel, is_moderator=False)

            # email verification stuff
            messages.success(request, send_email(request,signup_form.cleaned_data.get("email")))

            username = signup_form.cleaned_data.get("username")
            user.save()
            messages.success(request, f"Account created for {username}. Please follow the instructions received by email to confirm your account.")
            return redirect("login-view")
        else: # invalid signup_form
            messages.error(request, 'Please correct the errors below.')
    else:
        signup_form = NewUserForm()
    context = {'form':signup_form}
    return render(request, 'signup.html', context)





def login_view(request):
    if request.user.is_authenticated:
        return redirect('home-view')
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



def send_pwd_reset_email(r,email):
    # this function should be silent to the user in order not to leak if email exists or not
    return r.build_absolute_uri(reverse("password-reset-view")) + gen_email_token(email)



def password_reset_form(request):
    if request.method == 'POST':
        form_email = request.POST["pwd_reset_email"]
        messages.success(request,"If the provided email address links to an activated account on the platform, a password reset email has been sent.")
        user_if_exists = NexusUser.objects.filter(email=form_email)
        if user_if_exists:
            if user_if_exists[0].is_active:
                messages.success(request,send_pwd_reset_email(request,form_email))
    return render(request, 'password_reset_form.html')



def password_reset(request,token):
    if request.method == 'POST': # clicked on the change my password button
        pass 
    else: # user has clicked on the email reset link
        try: # verify if the token is valid
            user_email_dict = TimestampSigner().unsign_object(urlsafe_b64decode(token).decode(),max_age=password_reset_delay)
            user = NexusUser.objects.filter(email=user_email_dict["email"])[0]
            context = {'form':Password_change_form}
            return render(request,"password_reset.html",context = context) # return the password reset form
        except SignatureExpired: # reset link is expired
            messages.error(request, 'This password reset link is expired, please acquire a new one')
            return redirect('password-reset-view') # return to forgot your password
            

        except BadSignature: # bad link
            messages.error(request, 'This password reset link is invalid')
            return redirect('password-reset-view')

        except Exception:
            messages.error(request, 'Something went wrong :(')
            return redirect('password-reset-view')
        
def account_view(request):
    return render(request, 'account.html', )