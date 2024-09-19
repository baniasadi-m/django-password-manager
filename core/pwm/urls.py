from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

app_name = "pwm"

urlpatterns = [
    path('', views.index, name='fbv-index'),
    path("mba/", views.IndexView.as_view(), name='cbv-index'),
    path("google/", views.RedirecToMaktab.as_view(), name='cbv-index'),
]