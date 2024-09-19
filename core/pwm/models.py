from django.db import models

# Create your models here.


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
