from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home_view,name="home-view"),
    path("create/", views.new_channel, name="new-channel"),
    path("m/<slug>", views.show_channel, name="show-channel"),
]