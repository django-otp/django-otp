from django.contrib import admin
import django.contrib.auth.views
from django.http import HttpResponse
from django.urls import path
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
    path('', HomeView.as_view()),

    path('login/', django_otp.views.LoginView.as_view()),
    path('logout/', django.contrib.auth.views.LogoutView.as_view()),

    path('admin/', admin.site.urls),
    path('otpadmin/', otp_admin_site.urls),
]
