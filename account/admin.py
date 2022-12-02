from django.contrib import admin
# Register your models here.
from .models import *
class ClientAdmin(admin.ModelAdmin):
    list_display=['client_id','client_name','company_name']

class LicenseAdmin(admin.ModelAdmin):
    list_display=['client_id','license_id','active_license']

admin.site.register(Client,ClientAdmin)
admin.site.register(License,LicenseAdmin)