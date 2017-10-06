# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

"""bbr3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from home import views as home_views

urlpatterns = [
    url(r'^$', home_views.home),
    url(r'^faq/$', home_views.faq),
    url(r'^aboutus/$', home_views.about),
    url(r'^privacy/$', home_views.cookies),

    url(r'^bands/', include('bands.urls')),
    url(r'^bbradmin/', admin.site.urls),
]
