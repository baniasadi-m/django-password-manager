from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile,UserTOTP,UserActivityLog


class CustomUserAdmin(UserAdmin):
    """
    Custom admin panel for user management with add and change forms plus password
    """

    model = User
    list_display = ("email", "is_superuser", "is_active", "is_verified")
    list_filter = ("email", "is_superuser", "is_active", "is_verified")
    searching_fields = ("email",)
    ordering = ("email",)
    fieldsets = (
        (
            "Authentication",
            {
                "fields": ("email", "password"),
            },
        ),
        (
            "permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                ),
            },
        ),
        (
            "group permissions",
            {
                "fields": ("groups", "user_permissions"),
            },
        ),
        (
            "important date",
            {
                "fields": ("last_login",),
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                ),
            },
        ),
    )

class UserTOTPAdmin(admin.ModelAdmin):
    
    list_display=['user','totp_secret','qr_code_image']

class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'path', 'method', 'ip_address', 'timestamp', 'action_description')
    list_filter = ('user', 'method', 'timestamp')
    search_fields = ('user__username', 'path', 'action_description')
admin.site.register(Profile)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserTOTP, UserTOTPAdmin)
admin.site.register(UserActivityLog, UserActivityLogAdmin)
