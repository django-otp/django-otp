from django.contrib import admin
import django.contrib.auth.views
from django.urls import path

from django_otp.admin import OTPAdminSite
import django_otp.views

from . import views


otp_admin_site = OTPAdminSite(OTPAdminSite.name)
for model_cls, model_admin in admin.site._registry.items():
    otp_admin_site.register(model_cls, model_admin.__class__)


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('about/', views.About.as_view(), name='about'),

    path('login/', django.contrib.auth.views.LoginView.as_view(), name='login'),
    path('logout/', django.contrib.auth.views.LogoutView.as_view(), name='logout'),
    path('login-otp/', django_otp.views.LoginView.as_view(), name='login-otp'),

    path('require-login/', views.require_login, name='require-login'),
    path('require-otp/', views.require_otp, name='require-otp'),
    path('require-login-then-otp/', views.require_login_then_otp, name='require-login-then-otp'),

    path('admin/', admin.site.urls),
    path('otpadmin/', otp_admin_site.urls),
]
