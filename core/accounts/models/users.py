from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password and extra data.
        """
        if not email:
            raise ValueError(_("the Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model for authentication management through email address instead of username
    """

    email = models.EmailField(max_length=255, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __str__(self):
        return self.email
    


class UserTOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    totp_secret = models.CharField(max_length=100, blank=True, null=True)
    # qr_code_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)  
    qr_code_image = models.BinaryField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.email} TOTP Secret'



class UserActivityLog(models.Model):
    class Meta:
        verbose_name = "گزارش "
        verbose_name_plural = "گزارشات"
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    path = models.CharField(max_length=500)  # URL path accessed by the user
    method = models.CharField(max_length=10)  # HTTP method (GET, POST, etc.)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # User's IP address
    timestamp = models.DateTimeField(default=timezone.now)  # Time of the activity
    action_description = models.TextField(null=True, blank=True)  # Description of the activity

    def __str__(self):
        return f"{self.user} - {self.action_description} on {self.timestamp}"
