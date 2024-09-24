from django.urls import path, include
from . import views

app_name = "accounts"

urlpatterns = [

    path("", include("django.contrib.auth.urls")),
    path("send-email/", views.send_email, name="send-email"),
    path("test/", views.test, name="test"),
    path('totp_generate/', views.GenerateTOTPView.as_view(), name='totp_generate'),
    path('totp_verify/', views.VerifyTOTPView.as_view(), name='totp_verify'),
    path('totp_success/', views.TOTPSuccessView.as_view(), name='totp_success'),
    path('totp_show/', views.TOTPShowView.as_view(), name='totp_show'),
    # path('setup2fa/',views.AdminSetupTwoFactorAuthView.as_view())
    # path('api/v1/',include('accounts.api.v1.urls')),
    # path("api/v2/", include("djoser.urls")),
    # path("api/v2/", include("djoser.urls.jwt")),
]
