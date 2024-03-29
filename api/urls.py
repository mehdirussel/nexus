"""
URL configuration for nexus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('user-channels/',views.UserChannelsAPIView.as_view(),name='api-hello-view'),
    path('channel-messages/<channel_id>/', views.ChannelMessagesAPIView.as_view(), name='channel-messages-api'),
    path('channel-details/<id>/', views.ChannelDetailAPIView.as_view(), name='channel-details-api'),
    path("send-message/", views.send_msg_api, name="send-message-api"),
    path('mark-message-as-read/<message_id>/', views.mark_message_read_api, name='mark-message-as-read-api'),
    path('channel-new-messages/<channel_id>/', views.ChannelUnreadMessagesAPIView.as_view(), name='channel-new-messages-api'),  
    path('delete-msg/<message_id>/', views.delete_msg, name='delete-message-api'),
    
]
