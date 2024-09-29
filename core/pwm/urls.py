from django.urls import path, include
# from .views import UserRegisterView,DashboardView,IndexView, EditProfileView
from . import views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.contrib.auth.views import LoginView, LogoutView


app_name = "pwm"

urlpatterns = [
    path("", LoginView.as_view(template_name='pwm/login.html'), name='login'),
    path("search/", views.IndexView.as_view(), name='search'),
    path("register/", views.UserRegisterView.as_view(), name='register'),
    path("register/profile", views.ProfileRegisterView.as_view(), name='register_profile'),
    path("logout/", LogoutView.as_view(), name='logout'),
    path('dashboard/',views.DashboardView.as_view(),name='dashboard'),
    path('edit_profile/', views.EditProfileView.as_view(), name='edit_profile'),
    path('resetpass/', views.ResetPassView.as_view(), name='resetpass'),
    path('resetpass_result/', views.ResetPassResultView.as_view(), name='resetpass_result'),
    path('checkMobile/', views.MobileCheckView.as_view(), name='checkmobile'),
    path('verifyMobile/', views.MobileVerifyView.as_view(), name='verifymobile'),
    path('userStatus/', views.UserStatusView.as_view(), name='userstatus'),
    
    # path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    # path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    # path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    # path("login/", views.RedirecToMaktab.as_view(), name='cbv-index'),
    # path("resetpass/", views.RedirecToMaktab.as_view(), name='cbv-index'),
    # path("google/", views.RedirecToMaktab.as_view(), name='cbv-index'),
    # path("google/", views.RedirecToMaktab.as_view(), name='cbv-index'),
]