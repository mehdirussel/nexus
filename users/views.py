from django.shortcuts import render,redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login,authenticate
from django.contrib.auth.views import LoginView
from .my_forms import NewUserForm,Password_change_form, EditUserForm
from .models import NexusUser
from channels.models import Channel,perms_user_channel_rel
from django.core.signing import TimestampSigner,BadSignature,SignatureExpired
from base64 import urlsafe_b64encode,urlsafe_b64decode
from django.core.mail import send_mail

password_reset_delay = 10*60 # 10 minutes (in seconds)


def gen_email_token(email):
    timestamp_token = TimestampSigner().sign_object({"email":email})
    email_verif_token = urlsafe_b64encode(timestamp_token.encode()).decode()
    
    return email_verif_token


def send_verif_email(r,email):
    verif_link = r.build_absolute_uri(reverse("empty-verify-view")) + gen_email_token(email)
    email_content = f""" 
    Email verification

    To verify your email address, please click on the link below:

    {verif_link}

    """
    is_sent = send_mail(
                'Verify your email address',
                email_content,
                None,
                [email],
                fail_silently=False)

    if is_sent == 0:
        messages.error(r,'The verification email could not be sent, please contact an admin')

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
            send_verif_email(request,signup_form.cleaned_data.get("email"))

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
            if user.is_disabled:
                messages.error(request, 'Login failed! Your account has been deleted.')
            else:
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


        
def account_view(request):
    return render(request, 'account.html', )

def account_modify(request):
    try:
        user_instance = NexusUser.objects.get(username=request.user.username)
        old_email = user_instance.email
    except NexusUser.DoesNotExist:
        # Gérer le cas où NexusUser n'existe pas pour cet utilisateur
        # Peut-être créer un nouveau NexusUser ici si nécessaire
        pass

    if request.method == 'POST':
        form = EditUserForm(request.POST, request.FILES, instance=user_instance)
        if form.is_valid():
            
            # si a changé l email
            if old_email != form.cleaned_data.get("email"):
                # envoi nouveau email verification
                send_verif_email(request,form.cleaned_data.get("email"))
                user_instance.is_active=False # desactiver son compte jusqua activation apr mail
                user_instance.save()
                return redirect(f'/users/logout/')

            form.save()
            return redirect(f'/users/account/')  # Redirigez l'utilisateur vers une vue de profil ou une autre page après la modification
    else:
        form = EditUserForm(instance=user_instance)
    return render(request, 'account_modify.html', {'form': form})

def account_delete(request):
    if request.method == 'POST':
        # Supprimer le compte de l'utilisateur actuel
        request.user.is_disabled = True # pour ne pas perdre les anciennes conversations, on ne supprime pas les users
        request.user.save()
        # Déconnecter l'utilisateur après suppression
        return redirect('logout-view')  # Rediriger vers la page d'accueil ou une autre vue
    return render(request, 'account_delete.html')
