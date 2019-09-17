from __future__ import absolute_import, division, print_function, unicode_literals

from django.conf.urls import url
from django.contrib import admin
import django.contrib.auth.views
from django.http import HttpResponse
from django.views.generic.base import View

import django_otp.views


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(request.user.get_username())


urlpatterns = [
    url(r'^$', HomeView.as_view()),
    url(r'^login/$', django_otp.views.LoginView.as_view()),
    url(r'^logout/$', django.contrib.auth.views.LogoutView.as_view()),
    url(r'^admin/', admin.site.urls),
]
