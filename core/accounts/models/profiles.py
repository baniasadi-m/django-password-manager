from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from .users import User
# from ...pwm.models import WinServer

class Profile(models.Model):
    """
    Profile class for each user which is being created to hold the information
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nid = models.CharField(blank=True,unique=True, max_length=20,verbose_name="کد ملی")
    first_name = models.CharField(blank=True,max_length=250,verbose_name="نام")
    last_name = models.CharField(blank=True,max_length=250,verbose_name="نام خانوادگی")
    mobile = models.CharField(blank=True,unique=True,max_length=15,verbose_name="شماره موبایل")
    # mobile_verified = models.BooleanField(default=False)
    image = models.ImageField(blank=True, null=True,verbose_name='عکس کاربر')
    description = models.TextField(blank=True,verbose_name='توضیحات')
    created_date = models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_date = models.DateTimeField(auto_now=True,verbose_name='آخرین بروزرسانی')
    server = models.ForeignKey('pwm.WinServer',blank=True,null=True,on_delete=models.DO_NOTHING,verbose_name='سرور')
    win_local_account = models.CharField(max_length=50,blank=True,verbose_name='اکانت local')
    win_ldap_account = models.CharField(max_length=50,blank=True,verbose_name='اکانت ldap')
    
    def __str__(self):
        return self.user.email


@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    """
    Signal for post creating a user which activates when a user being created ONLY
    """
    if created:
        Profile.objects.create(user=instance)