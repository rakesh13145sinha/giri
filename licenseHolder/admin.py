from django.contrib import admin
from .models import *

# Register your models here.
class EmployeeAdmin(admin.ModelAdmin):
    list_display=['client_id','employee_name','employeeId']

class VendorAdmin(admin.ModelAdmin):
    list_display=['vendor_name','vendorId']

class MaterialAdmin(admin.ModelAdmin):
    list_display=['client_id','material_name','materialId']

class ProjectAdmin(admin.ModelAdmin):
    list_display=['client_id','project_name','projectId']

class ClientSeftyCheckListAdmin(admin.ModelAdmin):
    list_display=['id','client_id','select_sefty_checklist']

class ClientQualityCheckListAdmin(admin.ModelAdmin):
    list_display=['id','client_id','select_quality_checklist']


admin.site.register(Employee,EmployeeAdmin)
admin.site.register(Vendor,VendorAdmin)
admin.site.register(Project,ProjectAdmin)
admin.site.register(NonComplianceReport)
admin.site.register(ClientSeftyCheckList,ClientSeftyCheckListAdmin)
admin.site.register(ClientQualityCheckList,ClientQualityCheckListAdmin)
admin.site.register(Material,MaterialAdmin)
admin.site.register(SaveOtp)
admin.site.register(InspectionDetail)
admin.site.register(InspectAreaQuestion)
admin.site.register(ObservationReportImage)
admin.site.register(NonComplianceReportImage)
admin.site.register(SiteObservationReport)

