from django.conf.urls import url
from django.contrib import admin
import django.contrib.auth.views
from django.http import HttpResponse
from django.views.generic.base import View

import django_otp.views
from django_otp.admin import OTPAdminSite


otp_admin_site = OTPAdminSite(OTPAdminSite.name)
for model_cls, model_admin in admin.site._registry.items():
    otp_admin_site.register(model_cls, model_admin.__class__)


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(request.user.get_username())


urlpatterns = [
    url(r'^$', HomeView.as_view()),
    url(r'^login/$', django_otp.views.LoginView.as_view()),
    url(r'^logout/$', django.contrib.auth.views.LogoutView.as_view()),
    url(r'^admin/', otp_admin_site.urls),
]
