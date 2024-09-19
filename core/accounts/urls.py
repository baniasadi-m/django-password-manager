from django.urls import path, include
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/",include(),name='login'),
    path("logout/", include(),name='logout'),
    path("", include("django.contrib.auth.urls")),
    path("send-email/", views.send_email, name="send-email"),
    path("test/", views.test, name="test"),
    # path('api/v1/',include('accounts.api.v1.urls')),
    path("api/v2/", include("djoser.urls")),
    path("api/v2/", include("djoser.urls.jwt")),
]
