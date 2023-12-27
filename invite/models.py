from django.db import models
from django.core.signing import TimestampSigner,BadSignature,SignatureExpired
from base64 import urlsafe_b64encode,urlsafe_b64decode
from channels.models import Channel


def gen_inv_token(ch_id):
    timestamp_token = TimestampSigner().sign_object({"channel_id":ch_id})
    return urlsafe_b64encode(timestamp_token.encode()).decode()



