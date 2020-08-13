from django.contrib import admin
import django.contrib.auth.views
from django.http import HttpResponse
from django.views.generic.base import View

from django_otp.admin import OTPAdminSite
import django_otp.views

try:
    from django.urls import re_path
except ImportError:  # Django < 2.0
    from django.conf.urls import url as re_path


otp_admin_site = OTPAdminSite(OTPAdminSite.name)
for model_cls, model_admin in admin.site._registry.items():
    otp_admin_site.register(model_cls, model_admin.__class__)


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(request.user.get_username())


urlpatterns = [
    re_path(r'^$', HomeView.as_view()),

    re_path(r'^login/$', django_otp.views.LoginView.as_view()),
    re_path(r'^logout/$', django.contrib.auth.views.LogoutView.as_view()),

    re_path(r'^admin/', admin.site.urls),
    re_path(r'^otpadmin/', otp_admin_site.urls),
]
