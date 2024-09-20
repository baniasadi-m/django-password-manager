from django.contrib import admin
from .models import WinServer,LicenseInfo,WorkingHours
# Register your models here.


class WinServerAdmin(admin.ModelAdmin):
    list_display =['name','ip','ldap_domain','is_ldap','is_enabled']

class LicenseInfoAdmin(admin.ModelAdmin):
    list_display = ['company_short_name','company_name','limit_user','expired_at']
   
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ['start_time','end_time','weekdays']
     
admin.site.register(WorkingHours,WorkingHoursAdmin)
admin.site.register(LicenseInfo,LicenseInfoAdmin)
admin.site.register(WinServer,WinServerAdmin)