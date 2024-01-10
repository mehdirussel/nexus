from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home_view,name="home-view"),
    path("create/", views.new_channel, name="new-channel"),
    path("m/<slug>", views.show_channel, name="show-channel"),
    path("m/<slug>/options", views.options_channel, name="options-channel"),
    path("m/<slug>/delete", views.delete_channel, name="delete-channel"),
    path("m/<slug>/modify", views.modify_channel, name="modify-channel"),
    path('change-user-role/<uuid:channel_id>/', views.change_user_role, name='change-user-role'),
]