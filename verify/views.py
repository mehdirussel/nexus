from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.core.signing import TimestampSigner,BadSignature,SignatureExpired
from base64 import urlsafe_b64decode
from users.models import NexusUser

email_verification_delay = 2*24*3600 # 2 days (in seconds)
DEST_AFTER_VALIDATION = 'login.html'
DEST_IF_FAILED = 'login.html'

def validate_token(request,token_to_check):
    try:
        user_to_validate = TimestampSigner().unsign_object(urlsafe_b64decode(token_to_check).decode(),max_age=email_verification_delay) #7 jours
        user = get_object_or_404(NexusUser,email=user_to_validate["email"])
        user.is_active = True
        user.save()
        messages.success(request, 'Email verififed!')
        return render(request, DEST_AFTER_VALIDATION)
    except SignatureExpired:
        messages.error(request, 'This verification link is expired')
        return render(request, DEST_IF_FAILED)
    except Exception:
        messages.error(request, 'Invalid email verification link')
        return render(request, DEST_IF_FAILED)