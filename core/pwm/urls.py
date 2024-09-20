from django.urls import path, include
from .views import UserRegisterView,DashboardView,IndexView
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.contrib.auth.views import LoginView, LogoutView


app_name = "pwm"

urlpatterns = [
    path("", LoginView.as_view(template_name='pwm/login.html'), name='login'),
    path("search/", IndexView.as_view(), name='search'),
    path("register/", UserRegisterView.as_view(), name='register'),
    path("logout/", LogoutView.as_view(), name='logout'),
    path('dashboard/',DashboardView.as_view(),name='dashboard'),
    # path("login/", views.RedirecToMaktab.as_view(), name='cbv-index'),
    # path("resetpass/", views.RedirecToMaktab.as_view(), name='cbv-index'),
    # path("google/", views.RedirecToMaktab.as_view(), name='cbv-index'),
    # path("google/", views.RedirecToMaktab.as_view(), name='cbv-index'),
]