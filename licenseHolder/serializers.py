from rest_framework import serializers
from account.models import *
from licenseHolder.models import *

class Employeeserializers(serializers.ModelSerializer):
    class Meta:
        model=Employee
        fields=["id",'employee_name','phone_number','email','employeeId','create_date','employee_status']


class Venderserializers(serializers.ModelSerializer):
    class Meta:
        model=Vendor
        fields='__all__'


class Materialserializers(serializers.ModelSerializer):
    class Meta:
        model=Material
        fields='__all__'

class Projectserializers(serializers.ModelSerializer):
    class Meta:
        model=Project 
        exclude=['assigned_employee','assigned_material']

class Planserializers(serializers.ModelSerializer):
    class Meta:
        model=Plan 
        fields='__all__'

class Projectserializers(serializers.ModelSerializer):
    class Meta:
        model=Project 
        exclude=['client_id','assigned_employee','assigned_material','vendor','quality','sefty']

class InspectAreaQuestionserializers(serializers.ModelSerializer):
    class Meta:
        model=InspectAreaQuestion 
        fields="__all__"
class RescheduleInspectserializers(serializers.ModelSerializer):
    class Meta:
        model=RescheduleInspect 
        fields="__all__"

class Rescheduleserializers(serializers.ModelSerializer):
    class Meta:
        model=RescheduleInspect 
        exclude=['status',"inspection","client_id"]

class InspectionDetailserializers(serializers.ModelSerializer):
    class Meta:
        model=InspectionDetail 
        exclude=['project',"material_inspected","vendor"]
        
class SiteObservationReportserializers(serializers.ModelSerializer):
    class Meta:
        model=SiteObservationReport 
        fields='__all__'
        
class SiteObservationGetserializers(serializers.ModelSerializer):
    class Meta:
        model=SiteObservationReport 
        exclude=('client_id','project','vendorId')
        
        
class NCRserializers(serializers.ModelSerializer):
    class Meta:
        model=NonComplianceReport 
        fields='__all__'
        
class NCRGetserializers(serializers.ModelSerializer):
    class Meta:
        model=NonComplianceReport 
        exclude=('client_id','project','vendorId')