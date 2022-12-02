from distutils.command.upload import upload
from telnetlib import STATUS
from django.db import models
from django.db.models.fields.json import CaseInsensitiveMixin
from AdminUser.models import QualityQuestion, SeftyQuestion
from account.models import License
from account.models import *
# Create your models here.


class Plan(models.Model):
    plan_name=models.CharField(max_length=50)
    cost=models.CharField(max_length=20)
    about_plan=models.TextField()
    create_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    
    def __str__(self):

        return self.plan_name

class SaveOtp(models.Model):
    contact=models.CharField(max_length=255)
    otp=models.IntegerField()
    def __str__(self):
        return self.contact

class Employee(models.Model):
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    employee_name=models.CharField(max_length=100,null=True)
    email=models.EmailField()
    phone_number=models.CharField(max_length=20,null=True)
    employeeId=models.CharField(max_length=100,unique=True)
    assigned_license=models.ForeignKey(License,related_name='assigned_license',on_delete=models.CASCADE,null=True)
    phone_number_status=models.BooleanField(default=False)
    employee_status=models.BooleanField(default=True)
    create_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)

    def __str__(self):
        return self.employee_name

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.title)
    #     super(Employee, self).save(*args, **kwargs)

class Vendor(models.Model):
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    vendor_name=models.CharField(max_length=100)
    email=models.EmailField()
    contact_no=models.CharField(max_length=20)
    address=models.TextField()
    supervisor_name=models.CharField(max_length=100)
    supervisor_contact=models.CharField(max_length=100)
    vendorId=models.CharField(max_length=50,null=True,unique=True)
    vender_status=models.BooleanField(default=True)
    create_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)

    def __str__(self):
        return self.vendor_name

class Material(models.Model):
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    material_name=models.CharField(max_length=100)
    description=models.TextField()
    BOQ=models.CharField(max_length=100)
    #make=models.ForeignKey(Vendor,on_delete=Vendor)
    UOM=models.CharField(max_length=200)
    Total_Quantity=models.CharField(max_length=200)
    Baseline_Quantity=models.CharField(max_length=200)
    materialId=models.CharField(max_length=100,unique=True)
    material_status=models.BooleanField(default=True)
    create_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)


    def __str__(self):
        return self.materialId


class ClientQualityCheckList(models.Model):
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    select_quality_checklist=models.OneToOneField(QualityCheckList,on_delete=models.CASCADE)
    quality_question=models.ManyToManyField(QualityQuestion,related_name="quality_question")
    status=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)

    def __str__(self) :
        return self.select_quality_checklist.name

class ClientSeftyCheckList(models.Model):
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    select_sefty_checklist=models.OneToOneField(SeftyCheckList,on_delete=models.CASCADE)
    sefty_question=models.ManyToManyField(SeftyQuestion,related_name="sefty_question")
    status=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)

    def __str__(self) :
        return self.select_sefty_checklist.name

class Project(models.Model):
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    project_name=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    approver=models.CharField(max_length=100,null=True,blank=True)#name of employee
    approverid=models.CharField(max_length=100,null=True,blank=True)
    
    projectId=models.CharField(max_length=100,unique=True)
    project_status=models.BooleanField(default=True)

    assigned_employee=models.ManyToManyField(Employee,related_name="Employee")
    assigned_material=models.ManyToManyField(Material,related_name="materila")
    vendor=models.ManyToManyField(Vendor,related_name="asigned_vender")
    quality=models.ManyToManyField(ClientQualityCheckList,related_name="quality_check_list")
    sefty=models.ManyToManyField(ClientSeftyCheckList,related_name="safty_check_list")
    create_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    update_date=models.DateTimeField(auto_now=True,auto_now_add=False)

    def __str__(self):
        return self.projectId

#for quality
class InspectionDetail(models.Model):
    CHOICES=[("Rejected","R"),("Approved","A"),("Progress","P")]
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    area_inspected=models.CharField(max_length=255)
    material_inspected=models.ForeignKey(Material,on_delete=models.CASCADE,null=True)
    material_quantity=models.CharField(max_length=255)
    material_unit=models.CharField(max_length=255)
    vendor=models.ForeignKey(Vendor,on_delete=models.CASCADE)
    employee=models.CharField(max_length=220,null=True,blank=True)
    #approver_status=models.BooleanField(default=False)
    reportid=models.CharField(max_length=100,null=True)
    approver_status=models.CharField(max_length=50, choices=CHOICES,default="Progress",null=True)
    status=models.BooleanField(default=False)
    create_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)
    update_date=models.DateTimeField(auto_now=True,auto_now_add=False)
    def __str__(self):
        return str(self.id)

#for quality question 
class InspectAreaQuestion(models.Model):
    inspection=models.ForeignKey(InspectionDetail,on_delete=models.CASCADE)
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    question=models.ForeignKey(QualityQuestion,on_delete=models.CASCADE)
    complite_status=models.BooleanField(default=False)
    approver_status=models.BooleanField(default=False)
    not_complite_resion=models.CharField(max_length=220,null=True,blank=True)
    create_date=models.DateTimeField(auto_now=True,auto_now_add=False)
    def __str__(self):
        return self.project.project_name

class InspectAreaQuestionimage(models.Model):
    inspection=models.ForeignKey(InspectionDetail,on_delete=models.CASCADE)
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="area/image")
    create_date=models.DateTimeField(auto_now=True,auto_now_add=False)
    def __str__(self):
        return "%s %s %s" %(self.project,self.client_id,self.inspection)

"""ReInspect """
class RescheduleInspect(models.Model):
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    inspection=models.ForeignKey(InspectionDetail,on_delete=models.CASCADE)
    schedule_date=models.DateField()
    schedule_time=models.TimeField()
    status=models.BooleanField(default=False)
    create_date=models.DateTimeField(auto_now=True,auto_now_add=False,null=True)


class ReportDoc(models.Model):
    inspection=models.ForeignKey(InspectionDetail,on_delete=models.CASCADE)
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    document=models.FileField(upload_to="inspection/image")
    create_date=models.DateTimeField(auto_now=True,auto_now_add=False)
    update_date=models.DateTimeField(auto_now=True,auto_now_add=False)
    def __str__(self):
        return "%s %s %s" %(self.project,self.client_id,self.inspection)
    


class SiteObservationReport(models.Model):
    CATEGORY=[('Quality','Quality'),('Safety','Safety'),('Housekeeping',"Housekeeping")]
    SEVERITY_LEVEL=[('High','High'),('Medium','Medium'),('Low','Low')]
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    vendorId=models.ForeignKey(Vendor,on_delete=models.CASCADE)
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    area_inspected=models.TextField()
    add_observation=models.TextField()
    category=models.CharField(max_length=50,choices=CATEGORY)
    observatation_status=models.BooleanField(default=True)
    severity_level=models.CharField(max_length=50,choices=SEVERITY_LEVEL)
    siteobsevationid=models.CharField(max_length=200,null=True,blank=True)
    
    
class ObservationReportImage(models.Model):
    #obsevation_report=models.ForeignKey(SiteObservationReport,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='obsevation/report')
    site_image_id=models.CharField(max_length=200,null=True,blank=True)

class NonComplianceReport(models.Model):
    CATEGORY=[('Quality','Quality'),('Safety','Safety'),('Housekeeping',"Housekeeping")]
    SEVERITY_LEVEL=[('High','High'),('Medium','Medium'),('Low','Low')]
    client_id=models.ForeignKey(Client,on_delete=models.CASCADE)
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
    area_inspected=models.TextField()
    vendorId=models.ForeignKey(Vendor,on_delete=models.CASCADE)
    category=models.CharField(max_length=50,choices=CATEGORY)
    severity_level=models.CharField(max_length=50,choices=SEVERITY_LEVEL)
    root_causer=models.TextField()
    contract_clauser_no=models.CharField(max_length=250)
    corrective_action=models.TextField()
    ncr_status=models.BooleanField(default=True)
    ncrid=models.CharField(max_length=200,null=True,blank=True)
    
    
class NonComplianceReportImage(models.Model):
    #ncr_report=models.ForeignKey(NonComplianceReport,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='ncr/report')
    ncr_image_id=models.CharField(max_length=200,null=True,blank=True)