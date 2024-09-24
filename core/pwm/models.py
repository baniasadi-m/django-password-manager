from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.

class LicenseInfo(models.Model):
    class Meta:
        verbose_name = "لایسنس"
        verbose_name_plural = "لایسنس سامانه"
    company_short_name = models.CharField(blank=False, max_length=100,verbose_name="نام کوتاه سازمان")
    company_name = models.CharField(blank=True, max_length=100,verbose_name="نام سازمان")
    api_enabled = models.BooleanField(blank=True,default=False)
    limit_user = models.IntegerField(verbose_name="تعداد کاربر مجاز")
    expired_at = models.DateTimeField(blank=False, verbose_name="تاریخ انقضا")
    latest_check = models.DateTimeField(blank=False,auto_now_add=True,verbose_name='آخرین چک')
    
    def save(self, *args, **kwargs):
        if not self.pk and LicenseInfo.objects.exists():
            raise ValidationError("You can only have one License instance.")
        return super().save(*args, **kwargs)


class WorkingHours(models.Model):
    class Meta:
        verbose_name = "ساعت کاری"
        verbose_name_plural = "ساعت کاری سامانه"
    start_time = models.TimeField()  # Start of working hours
    end_time = models.TimeField()    # End of working hours
    weekdays = models.CharField(max_length=13, help_text="Comma-separated list of weekdays (e.g., '0,1,2,3,4' for Monday to Friday)")  # Days of the week
    def save(self, *args, **kwargs):
        if not self.pk and WorkingHours.objects.exists():
            raise ValidationError("You can only have one WorkingHours instance.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Working hours: {self.start_time} - {self.end_time}, Weekdays: {self.weekdays}"

class WinServer(models.Model):
    class Meta:
        verbose_name = "سرور "
        verbose_name_plural = "مشخصات سرور"
        
    name = models.CharField(blank=False,default='server',unique=True, max_length=255,verbose_name="نام سرور")
    ip = models.CharField(blank=False,default='123.456.789.123', max_length=25,verbose_name="آدرس سرور")
    port = models.CharField(blank=False,default='636', max_length=25,verbose_name="پورت سرور")
    proxy_user = models.CharField(blank=False,default='admin', max_length=25,verbose_name="نام کاربری")
    proxy_password = models.CharField(blank=False,default='changeme', max_length=25,verbose_name="کلمه عبور")
    ldap_domain = models.CharField(blank=True,default='example.local', max_length=25,verbose_name="دامنه")
    description = models.TextField(blank=True,default='test',verbose_name="توضیحات ")
    is_enabled = models.BooleanField(default=False,verbose_name="فعال")
    is_ldap = models.BooleanField(default=False,verbose_name="LDAP")
    created_at = models.DateTimeField(auto_now_add=True, max_length=100,verbose_name="تاریخ ایجاد سرور")
    updated_at = models.DateTimeField(auto_now=True, max_length=100,verbose_name="آخرین بروزرسانی")
    def __str__(self) :
        return self.name
    
class WinUser(models.Model):
    class Meta:
        verbose_name = "کاربری ویندوز "
        verbose_name_plural = "مشخصات کاربری ویندوز"
        
    name = models.CharField(blank=True,unique=True, max_length=255,verbose_name="نام اکانت")
    server = models.ForeignKey(WinServer,blank=True,on_delete=models.DO_NOTHING,verbose_name="نام سرور")
    is_ldap = models.BooleanField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, max_length=100,verbose_name="تاریخ ایجاد ")
    updated_at = models.DateTimeField(auto_now=True, max_length=100,verbose_name="آخرین بروزرسانی")
    def __str__(self) :
        return self.name