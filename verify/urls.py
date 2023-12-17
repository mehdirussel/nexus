from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('',RedirectView.as_view(url="/users/login/"),name='empty-verify-view'),
    path('<str:token_to_check>',views.validate_token,name='verify-view'),
]