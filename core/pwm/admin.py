from django.contrib import admin
from .models import WinServer,LicenseInfo,WorkingHours   #,WinUser,ServerSelection
# Register your models here.


class WinServerAdmin(admin.ModelAdmin):
    list_display =['name','ip','ldap_domain','is_ldap','is_enabled']

class LicenseInfoAdmin(admin.ModelAdmin):
    list_display = ['company_short_name','company_name','limit_user','expired_at']
   
class WorkingHoursAdmin(admin.ModelAdmin):
    list_display = ['start_time','end_time','weekdays']

class WinUserAdmin(admin.ModelAdmin):
    list_display = ['name','server','is_ldap']  
    
class ServerSelectionAdmin(admin.ModelAdmin):
    filter_horizontal = ['servers','accounts']  
    
# admin.site.register(ServerSelection,ServerSelectionAdmin)
admin.site.register(WorkingHours,WorkingHoursAdmin)
admin.site.register(WinServer,WinServerAdmin)
# admin.site.register(WinUser,WinUserAdmin)
admin.site.register(LicenseInfo,LicenseInfoAdmin)