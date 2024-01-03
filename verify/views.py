from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.signing import TimestampSigner,BadSignature,SignatureExpired
from base64 import urlsafe_b64decode
from users.models import NexusUser
from users.views import send_verif_email

email_verification_delay = 2*24*3600 # 2 days (in seconds)
DEST_AFTER_VALIDATION = 'login.html'
DEST_IF_FAILED = 'login.html'

def validate_token(request,token_to_check):
    try:
        user_to_validate = TimestampSigner().unsign_object(urlsafe_b64decode(token_to_check).decode(),max_age=email_verification_delay) #7 jours
        user = get_object_or_404(NexusUser,email=user_to_validate["email"])
        if not user.is_active: # if user hasnt already activated his account
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been verified! You can login')
        else:
            messages.error(request, 'Your account is already verified!')
        return render(request, DEST_AFTER_VALIDATION)
    except SignatureExpired: # verification link is expired
        user_with_expired_link = TimestampSigner().unsign_object(urlsafe_b64decode(token_to_check).decode(),max_age=360*24*3600) # 360 days,  big enough to always be verified
        user_expired = get_object_or_404(NexusUser,email=user_with_expired_link["email"])
        if not user_expired.is_active: # if user hasnt already activated his account, otherwise we shouldnt resend a new link
            send_verif_email(request,user_with_expired_link["email"])
            messages.error(request, 'This verification link is expired, a new one has been sent to your email address.')
        else:
            messages.error(request, 'Your account is already verified!')
        return render(request, DEST_IF_FAILED)
    except Exception:
        messages.error(request, 'Invalid email verification link')
        return render(request, DEST_IF_FAILED)