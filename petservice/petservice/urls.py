"""petservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
from django.urls import re_path as url

urlpatterns = [
    path("", views.index, name='index'),
    path("index",views.index),
    path("login",views.login, name="login"),
    path("logout",views.logout, name="logout"),
    path("join",views.join, name="join"),
    path("mypage",views.mypage, name="mypage"),
    path("member",views.member, name="member"),
    path("Medical",views.Medical, name="medical"),
    path("services",views.services, name="services"),
    path("img_upload",views.img_upload,name="img_upload"),
    url(r'^static/(?P<path>.*)$', serve, {'document_root':settings.STATIC_ROOT}),
]