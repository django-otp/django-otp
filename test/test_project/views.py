from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView

from django_otp.decorators import otp_required


class Home(TemplateView):
    template_name = "home.html"


class About(TemplateView):
    template_name = "about.html"


@login_required
def require_login(request):
    return HttpResponseRedirect(reverse('home'))


@otp_required
def require_otp(request):
    return HttpResponseRedirect(reverse('home'))


@login_required
@otp_required
def require_login_then_otp(request):
    return HttpResponseRedirect(reverse('home'))
