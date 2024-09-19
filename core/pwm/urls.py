from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

app_name = "pwm"

urlpatterns = [
    path('', views.LoginView.as_view(), name='index'),
    path("mba/", views.IndexView.as_view(), name='cbv-index'),
    path("google/", views.RedirecToMaktab.as_view(), name='cbv-index'),
]