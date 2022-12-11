
from functools import partial
from django.shortcuts import render,get_object_or_404
from numpy import False_


from rest_framework.views import APIView
from rest_framework.response import Response

from AdminUser.models import SeftyQuestion
from account import client
from account.models import *
from rest_framework import status

from account.serializers import *
from licenseHolder.serializers import *
from account.client import license_generate
from datetime import date,time,datetime, timedelta
from .models import *
from django.db.models import Q, query
from licenseHolder.employeeId import *
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from licenseHolder.send_otp import sending_otp
import random
#from .base64code import upload_image
import uuid
import base64
from django.core.files.base import ContentFile


"""CLIENT LICENCE GENERATE"""
class Licence(APIView):
    def get(self,request):
        clientid=request.GET.get('client_id')
        try:
            client=Client.objects.get(client_id=clientid,client_status=True,)
        except Exception as msg:
            return Response({"message":"client id not found","status":False},status=status.HTTP_400_BAD_REQUEST)
        liecenses=License.objects.filter(client_id=client,license_status=True,active_license=False)
        response={
                    
                    "license_status":[license.license_id for license in liecenses ],
                    
                }
        return Response(response,status=status.HTTP_200_OK)

        
       
    def post(self,request):
        clientid=request.GET.get('client_id')
        client_payment_status=request.GET.get('payment_status')

        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True
        try:
            client=Client.objects.get(client_id=clientid)
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
        
        if clientid and client_payment_status:

            numberoflicense=data['number_of_license']
            
            client.license_purchased += int(numberoflicense)

            ammount_per_license=int(data['price']) // int(numberoflicense)

            """CALCULATE START DATE AND END DATE"""
            start_date=date.today()
            end_date_year=start_date + timedelta(days=365)
            end_date_month=start_date+timedelta(days=30)

            if int(numberoflicense)>1:
                
                for i in range(1 ,int(numberoflicense)+1):
                    License.objects.create(client_id=client,license_id=license_generate(),
                                            price=ammount_per_license,
                                            subcription_plan=data['subcription_plan'],
                                            created_at=start_date,
                                            end_at = end_date_month if "M" == data['subcription_plan'] else end_date_year

                                            
                                            )
                client.client_status=True
                client.save()
                return Response({"massge":"License genereate","status":True},status=status.HTTP_200_OK)
            else:
                License.objects.create(client_id=client,license_id=license_generate(),
                                        price=ammount_per_license,
                                        subcription_plan=data['subcription_plan'],
                                        created_at=start_date,
                                        end_at = end_date_month if "M" == data['subcription_plan'] else end_date_year
                                        
                                        )
                client.client_status=True
                client.save()
                return Response({"massge":"License genereate","status":True},status=status.HTTP_200_OK)
        else:
            return Response({"message":"your payment status is pandding yet!.we can't issue the licencse now"},status=status.HTTP_400_BAD_REQUEST)


"""LICENSE DISTRIBUTION """
class Employee_Registration(APIView):
    def get(self,request):
        clientid=request.GET.get('client_id')
        employeeid=request.GET.get('employee_id')
        projectID=request.GET.get('project_id')
        
        response={}
        try:
            client=Client.objects.get(client_id=clientid)
        except Exception as msg:
            return Response({"message":str(msg)})

        if clientid is not None and employeeid is None and projectID is None:
            
            employees=Employee.objects.filter(client_id=client)
           
            
            if employees.exists():
                for employee in employees:
                    assigned_projects=Project.objects.filter(client_id=client, assigned_employee__id=employee.id)
                    serializers=Employeeserializers(employee,many=False).data
                    serializers.update({"assigned_license":employee.assigned_license.license_id})
                    serializers.update({"assigned_project":[{
                                            "project_id":project.projectId,
                                            "project_name":project.project_name
                                            } 
                                        for project in assigned_projects]})
                    response[employee.id]=serializers
                    
                return Response(response.values(),status=status.HTTP_200_OK)
            else:
                return Response(response.values(),status=status.HTTP_200_OK)

        elif employeeid is not None and clientid is not None and projectID is None:
            try:
                empolyee=Employee.objects.get(client_id=client,employeeId=employeeid)
            except Exception as msg:
                return Response({"massege":"employee id not found"},status=status.HTTP_404_NOT_FOUND)
            serializers=Employeeserializers(empolyee,many=False).data
            serializers.update({"assigned_license":empolyee.assigned_license.license_id})
            return Response(serializers,status=status.HTTP_200_OK)
        
        elif projectID is not None and clientid is not None:
            try:
                project=Project.objects.get(client_id=client,projectId=projectID)
            except Exception as msg:
                return Response({"massege":"project id not found","status":False},status=status.HTTP_404_NOT_FOUND)
            employee=project.assigned_employee.all()
            serializers=Employeeserializers(employee,many=True).data
            
            return Response(serializers,status=status.HTTP_200_OK)
        
        
        else:
            return Response({"message":"employee not found"},status=status.HTTP_400_BAD_REQUEST)

        
    def post(self,request):
        clientid=request.GET.get('client_id')
        licenseid=request.GET.get('license_id')
        data=request.data
        try:
            client=Client.objects.get(client_id=clientid)
        except Exception as msg:
            return Response({"message":str(msg)})
        try: 
            license=License.objects.get(Q(client_id=client,license_id=licenseid)  )
                                                                 
        except Exception as mes:
            
            return Response({"massage":"license id not found may be license already assigned"},status=status.HTTP_400_BAD_REQUEST)

        licenses_active=License.objects.filter(
                                        Q(client_id=client,license_id=licenseid,license_status=True,active_license=True)
                                           )

        if licenses_active.exists ():
            return Response({"message":"This license is already assign and in use","status":True},status=status.HTTP_400_BAD_REQUEST)

        licenses__status=License.objects.filter(
                                        Q(client_id=client,license_id=licenseid,license_status=False)
                                        
                                        )
        if licenses__status.exists ():
            return Response({"message":"This license is expire or not valid  yet","status":True},status=status.HTTP_400_BAD_REQUEST)
        
        check_phonenumber_has_license=Employee.objects.filter(phone_number=data['phone_number'],phone_number_status=True)
        
        if check_phonenumber_has_license.exists():
            return Response({"message":"Enter phone number already have one license","status":True},status=status.HTTP_400_BAD_REQUEST)
        
        elif check_phonenumber_has_license.exists()==False:
            Employee.objects.create(client_id=client,employee_name=data['employee_name'],email=data['email'],
                                    employeeId=employeeid_generate(),phone_number=data['phone_number'],
                                    assigned_license=license,phone_number_status=True,
                                    employee_status=data['employee_status']
                                    )
            license.active_license=True
            license.save()
            return Response({"message":"Employee has assigned license","status":True},status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error contact to developer","status":False},status=status.HTTP_400_BAD_REQUEST)

        
    def put(self,request):
        employeeid=request.GET.get('employee_id')
        if employeeid:
            try:
                employee=Employee.objects.get(employeeId=employeeid)
            except Exception as msg:
                return Response({"message":"employee id not found"},status=status.HTTP_400_BAD_REQUEST)
            serializers=Employeeserializers(employee,data=request.data,partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data,status=status.HTTP_200_OK)
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"key errors"},status=status.HTTP_400_BAD_REQUEST)

    def patch(self,request):
        clientId=request.GET.get('client_id')
        employeeId=request.GET.get('employee_id')
        projects=request.GET.get('project_id')
        res={}
        
        try:
            client=Client.objects.get(client_id=clientId)
        except Exception as msg:
            return Response({"message":"client id not found","required":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        try:
            employee=client.employee_set.get(employeeId=employeeId)
        except Exception as msg:
            return Response({"message":str(msg)})

        #assigned_project=Project.objects.filter(assigned_employee__id=employee.id)
        for project in projects.split(","):
            try:
                getproject=client.project_set.get(projectId=project)
            except Exception as msg:
                return Response({"message":str(msg)})

            
            if getproject.assigned_employee.filter(id=employee.id):
                #getproject.assigned_employee.remove(employee)
                pass
            else:

                getproject.assigned_employee.add(employee)
            
        return Response({"message":"project assigned updated","status":True},status=status.HTTP_200_OK)
        

             
    def delete(self,request):
        clientid=request.GET.get('client_id') 
        employeeID=request.GET.get('employee_id')
        client= Client.objects.get(client_id=clientid)  
        employee=client.employee_set.get(id=employeeID) 
        projects=client.project_set.filter(assigned_employee__id=employeeID)
        for project in projects:
            project.assigned_employee.remove(employee)
        employee.delete()
        return Response({"message":"employee deleted"})
        

"""ADD VENDOR """ 
class Vendor_Add(APIView):
    def get(self,request):
        clientid=request.GET.get('client_id')
        vendorid=request.GET.get('vendor_id')
        projectid=request.GET.get('project_id')#proj0001
        response={}
        if clientid is not None and projectid is None:
            try:
                client=Client.objects.get(client_id=clientid)
            except Exception as msg:
                return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
            vendors=Vendor.objects.filter(client_id=client,vender_status=True)
            for vendor in vendors:
                assigned_projects=Project.objects.filter(client_id=client,vendor__id=vendor.id)
                serializers=Venderserializers(vendor,many=False).data
                serializers.update({"assigned_project":[{
                                            "project_id":project.projectId,
                                            "project_name":project.project_name
                                            } for project in assigned_projects]})
                response[vendor.id]=serializers
            return Response(response.values(),status=status.HTTP_200_OK)
        
        elif vendorid is not None and projectid is None:
            try:
                vendor=Vendor.objects.get(vendorId=vendorid,vender_status=True)
            except Exception as msg:
                return Response({"message":"vendor id not found"},status=status.HTTP_400_BAD_REQUEST)
            
            serializers=Venderserializers(vendor,many=False)
            return Response(serializers.data,status=status.HTTP_200_OK)
        
        elif clientid is not None and projectid is not None:
            
            try:
                client=Client.objects.get(client_id=clientid)
            except Exception as msg:
                return Response({"message":"client id not found","status":False},status=status.HTTP_400_BAD_REQUEST)
            try:
                project=Project.objects.get(client_id=client,projectId=projectid,project_status=True)
            except Exception as msg:
                return Response({"message":"Project id not found","status":False},status=status.HTTP_400_BAD_REQUEST)
            vendors=project.vendor.all()   
            serializers=Venderserializers(vendors,many=True).data
            return Response(serializers,status=status.HTTP_200_OK)
        else:
            return Response({"message":"something error","status":False},status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        clientid=request.GET.get('client_id')
        try:
            client=Client.objects.get(client_id=clientid)
        except Exception as msg:
            return Response({"message":str(msg)})
        data=request.data 
        try:
            Vendor.objects.create(client_id=client,vendor_name=data['vendor_name'],
                                    email=data['email'],contact_no=data['contact_no'],
                                    address=data['address'],supervisor_name=data['supervisor_name'],
                                    supervisor_contact=data['supervisor_contact'],vendorId=vendor_generate()
                                    
                                    )
            return Response({"message":"vender successful added","status":True},status=status.HTTP_200_OK)
        except Exception as msg:
            return Response({"message":str(msg)})
    
    def put(self,request):
        vendorid=request.GET.get('vendor_id')
        try:
            vendor=Vendor.objects.get(vendorId=vendorid,vender_status=True)
        except Exception as msg:
            return Response({"message":"vendor id not found"},status=status.HTTP_400_BAD_REQUEST)
            
        serializers=Venderserializers(vendor,data=request.data,partial=True)
        if serializers.is_valid():
            serializers.save()

            return Response(serializers.data,status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_200_OK)
    def patch(self,request):
        clientId=request.GET.get('client_id')
        vendorID=request.GET.get('vendor_id')
        projects=request.GET.get('project_id')
        
        
        try:
            client=Client.objects.get(client_id=clientId)
        except Exception as msg:
            return Response({"message":"client id not found","required":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        try:
            vendor=client.vendor_set.get(vendorId=vendorID)
        except Exception as msg:
            return Response({"message":str(msg),"status":False},status=status.HTTP_404_NOT_FOUND)

       
        for project in projects.split(","):
            try:
                getproject=client.project_set.get(projectId=project)
            except Exception as msg:
                return Response({"message":str(msg)})
            if getproject.vendor.filter(id=vendor.id):
                #getproject.vendor.remove(vendor)
                pass
            else:

                getproject.vendor.add(vendor)
            
        return Response({"message":"project assigned updated","status":True},status=status.HTTP_200_OK)
    
    def delete(self,request):
        vendorid=request.GET.get('vendor_id')
        if vendorid :
            try:
                vendor=Vendor.objects.get(vendorId=vendorid)
                vendor.vender_status=False
                vendor.save()
                return Response({"message":"vender deactivated succussful",},status=status.HTTP_200_OK)
            except Exception as msg:
                return Response({"message":"vendor id not found"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"key error"},status=status.HTTP_400_BAD_REQUEST)
            


""" ADD MATERIAL METHOD GET POST PUT DELETE """           
class Material_Add(APIView):
    def get(self,request):
        clientid=request.GET.get('client_id')
        meterialid=request.GET.get('material_id')
        projectid=request.GET.get('project_id')#proj0001
        res={}
        if clientid is not None and projectid is None:
            try:
                client=Client.objects.get(client_id=clientid)
            except Exception as msg:
                return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
            matetials=Material.objects.filter(client_id=client,material_status=True)
            for material in matetials:
                assigned_projects=Project.objects.filter(client_id=client,assigned_material__id=material.id)
                serializers=Materialserializers(material,many=False).data
                #serializers.update({"make":material.make.vendorId,"vendor_name":material.make.vendor_name})
                serializers.update({"assigned_project":[{
                                            "project_id":project.projectId,
                                            "project_name":project.project_name
                                            } for project in assigned_projects]})
                
                res[material.id]=serializers
            return Response(res.values(),status=status.HTTP_200_OK)
        
        elif meterialid is not None :
            try:
                material=Material.objects.get(materialId=meterialid,material_status=True)
            except Exception as msg:
                return Response({"message":"material id not found"},status=status.HTTP_400_BAD_REQUEST)
            
            serializers=Materialserializers(material,many=False).data
            
            # serializers.update({"make":material.make.vendorId,"vendor_name":material.make.vendor_name})
            return Response(serializers,status=status.HTTP_200_OK)
        elif projectid is not None and clientid is not None:
            try:
                client=Client.objects.get(client_id=clientid)
            except Exception as msg:
                return Response({"message":"client id not found","status":False,"error":str(msg)},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                project=Project.objects.get(client_id=client,projectId=projectid,project_status=True)
            except Exception as msg:
                return Response({"message":"project id not found","status":False,"error":str(msg)},status=status.HTTP_400_BAD_REQUEST)
            matetials=project.assigned_material.all()
            serializers=Materialserializers(matetials,many=True).data
                
            return Response(serializers,status=status.HTTP_200_OK)
        else:
            return Response({"message":"somthing key wrong","status":False},status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request):
        clientid=request.GET.get('client_id')
        # vendorid=request.GET.get('make')
        try:
            client=Client.objects.get(client_id=clientid)
        except Exception as msg:
            return Response({"message":str(msg)})

        # try:
        #     vendor=Vendor.objects.get(vendorId=vendorid)
        # except Exception as msg:
        #     return Response({"message":"vendor id not found"},status=status.HTTP_400_BAD_REQUEST)
        data=request.data 
        try:
            Material.objects.create(client_id=client,material_name=data['material_name'],
                                    description=data['description'],BOQ=data['BOQ'],
                                    #make=vendor,
                                    UOM=data['UOM'],
                                    Total_Quantity=data['Total_Quantity'],
                                    Baseline_Quantity=data['Baseline_Quantity'],
                                    materialId=meterial_generate()
                                    
                                    )
            return Response({"message":"matetial successful added","status":True},status=status.HTTP_200_OK)
        except Exception as msg:
            return Response({"message":str(msg)},status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request):
        meterialid=request.GET.get('material_id')
        try:
            material=Material.objects.get(materialId=meterialid,material_status=True)
        except Exception as msg:
            return Response({"message":"vendor id not found"},status=status.HTTP_400_BAD_REQUEST)
            
        serializers=Materialserializers(material,data=request.data,partial=True)
        if serializers.is_valid():
            serializers.save()

            return Response(serializers.data,status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_200_OK)


    def patch(self,request):
        clientId=request.GET.get('client_id')
        materialId=request.GET.get('material_id')
        projects=request.GET.get('project_id')
        res={}
        
        try:
            client=Client.objects.get(client_id=clientId)
        except Exception as msg:
            return Response({"message":"client id not found","required":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        try:
            material=client.material_set.get(materialId=materialId)
        except Exception as msg:
            return Response({"message":str(msg)})

       
        for project in projects.split(","):
            try:
                getproject=client.project_set.get(projectId=project)
            except Exception as msg:
                return Response({"message":str(msg)})
            if getproject.assigned_material.filter(id=material.id):
                # getproject.assigned_material.remove(material)
                pass
            else:

                getproject.assigned_material.add(material)
            
        return Response({"message":"project assigned updated","status":True},status=status.HTTP_200_OK)
    
    def delete(self,request):
        meterialid=request.GET.get('material_id')
        if meterialid :
            try:
                material=Material.objects.get(materialId=meterialid,material_status=True).delete()
                # material.material_status=False
                # material.save()
                return Response({"message":"material deactivated succussful",},status=status.HTTP_200_OK)
            except Exception as msg:
                return Response({"message":"material id not found"},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"key error"},status=status.HTTP_400_BAD_REQUEST)
            

"""HERE WE ARE TAKE A NEW  PROJECT ,NO ANY MATERIAL,EMPLOYEE,VENDER ADDING """
class Project_Create(APIView):
    def get(self,request):
        clientid=request.GET.get('client_id')
        projectid=request.GET.get('project_id')
        employeeid=request.GET.get('employee_id')#EMP0001
        qualitychecklist=request.GET.get('qualitychecklist')#True,False
        saftychecklist=request.GET.get('saftychecklist')#True,False
        response={}

        
        try:
            client=Client.objects.get(client_id=clientid)
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
        
        if clientid is not None and projectid is None and employeeid is None:
            
            projects=Project.objects.filter(client_id=client).order_by('-create_date')
            for project in projects:
                serilizers=Projectserializers(project,many=False).data 
                serilizers.update({"material":[
                                {   "material_name":mat.material_name,
                                    "materialId":mat.materialId }
                     
                     for mat in project.assigned_material.all() 
                     
                     ] })
                serilizers.update({"employee":[ 
                                    {   "employee_name":emp.employee_name,
                                        "employeeId":emp.employeeId 
                                    }
                            
                            
                            for emp in project.assigned_employee.all() 
                            
                                ]})
                serilizers.update({"vendor":[ 
                                    {   'vendor_name':contractor.vendor_name,
                                        "vendorId":contractor.vendorId 
                                    } 
                                    for contractor in project.vendor.all() 
                                    
                                    ]})
                response[project.id]=serilizers
            
            return Response(response.values(),status=status.HTTP_200_OK)
        elif clientid is not None and employeeid is not None and projectid is None:
            assigned_project=Project.objects.filter(
                                client_id=client,
                                assigned_employee__employeeId=employeeid,
                                 project_status=True
                                    )

            serializers=Projectserializers(assigned_project,many=True)
            return Response(serializers.data)
        elif projectid is not None and clientid is not None and employeeid is None:
            try:
                project=Project.objects.get(client_id=client,projectId=projectid, project_status=True)
            except Exception as msg:
                return Response({"message":"projct id not found"},status=status.HTTP_400_BAD_REQUEST)
            
            serilizers=Projectserializers(project,many=False).data 
            serilizers.update({"material":[
                                {   "material_name":mat.material_name,
                                    "materialId":mat.materialId }
                     
                     for mat in project.assigned_material.all() 
                     
                     ] })
            serilizers.update({"employee":[ 
                                {   "employee_name":emp.employee_name,
                                    "employeeId":emp.employeeId 
                                }
                        
                        
                        for emp in project.assigned_employee.all() 
                        
                            ]})
            serilizers.update({"vendor":[ 
                                {   'vendor_name':contractor.vendor_name,
                                    "vendorId":contractor.vendorId 
                                } 
                                for contractor in project.vendor.all() 
                                
                                ]})
            
           
            return Response(serilizers,status=status.HTTP_200_OK)
         
        
        elif projectid is not None and clientid is not None and employeeid is not None:
            try:
                project=Project.objects.get(client_id=client,
                        projectId=projectid, project_status=True,
                        )
                

            except Exception as msg:
                return Response({"message":"projct id not found","required":str(msg)},status=status.HTTP_400_BAD_REQUEST)
            if project.assigned_employee.filter(employeeId=employeeid).exists()==False:
                return Response({"message":"you are not assigned in this project","status":False},status=status.HTTP_200_OK)
            if qualitychecklist is not None:
                for qua in project.quality.filter(status=True):
                    response[qua.id]={
                            
                               
                                "name":qua.select_quality_checklist.name, 
                                "qualityid":qua.select_quality_checklist.qualityid,
                            
                        
                                     } 
            elif saftychecklist is not None:
                for safty in project.sefty.filter(status=True):
                    response[safty.id]={
                                "name":safty.select_sefty_checklist.name, 
                                "saftychecklistid":safty.select_sefty_checklist.saftychecklistid,
                        } 


            return Response(response.values(),status=status.HTTP_200_OK)

        



    def post(self,request):
        clientId=request.GET.get('client_id')
        data=request.data 
       
        try:
            client=Client.objects.get(client_id=clientId)
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_404_NOT_FOUND)
        
        try:
            project=Project(
                            client_id=client,
                            project_name=data['project_name'],
                            city=data['city'],
                            
                            projectId=project_generate(),
                            project_status=data['project_status']
                            )
            project.save()
        except Exception as msg:
            return Response({"message":str(msg)})
        
        
        return Response({"message":"Project successful created"},status=status.HTTP_200_OK)
    
    """for only add approver employee id"""
    def put(self,request):
        projectid=request.GET.get('project_id')
        clientid=request.GET.get('client_id')
        
        try:
            client=Client.objects.get(client_id=clientid)
        except Exception as msg:
            return Response({"message":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        if clientid is not None and projectid is not None:
            
            project=Project.objects.get(client_id=client,projectId=projectid)
            serializers=Projectserializers(project,data=request.data,partial=True)
            if serializers.is_valid():
                serializers.save()
            
                return Response(serializers.data,status=status.HTTP_200_OK)
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"something key error"},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        clientid=request.GET.get('client_id')
        projectid=request.GET.get('project_id')
        try:
            client=Client.objects.get(client_id=clientid)
        except ObjectDoesNotExist as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)

        try:
            project=Project.objects.get(client_id=client,projectId=projectid, project_status=True)
            project.project_status=False
            project.save()
            return Response ({"message":"project deleted"},status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message":"projct id not found"},status=status.HTTP_400_BAD_REQUEST)


"""ADD,GET,UPDATE,DELETE QUALITY CHECK LIST assign project"""
class Add_Quality_CheakList(APIView):
    def get(self,request):
        clientid=request.GET.get('client_id')
        client_quality_checklistid=request.GET.get('quality_id')
        projectid=request.GET.get('project_id')
        employeeid=request.GET.get('employee_id')
        response={}
        try:
            client=Client.objects.get(client_id=clientid,status=True,client_status=True)
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)

       
        if clientid is not None and client_quality_checklistid is None and projectid is None:
            for qualitychecklist in client.clientqualitychecklist_set.all():
               
                response[qualitychecklist.id]={
                    "id":qualitychecklist.id,
                    "name":qualitychecklist.select_quality_checklist.name,
                    "qualityid":qualitychecklist.select_quality_checklist.qualityid,
                    "status":qualitychecklist.select_quality_checklist.activate,
                    "created_date":qualitychecklist.created_date,
                    "assign_project":[ 
                                        {
                                            "project_id":project.projectId,
                                            "project_name":project.project_name
                                            }
                                        for project in client.project_set.filter(quality=qualitychecklist)
                                             ]

                }
            return Response(response.values(),status=status.HTTP_200_OK)
       
        elif clientid is not None and client_quality_checklistid is  not None and projectid is None:
            try:
                qualitychecklist=QualityCheckList.objects.get(qualityid=client_quality_checklistid,status=True,activate=True)
                clientqualitychecklist=ClientQualityCheckList.objects.get(client_id=client,select_quality_checklist=qualitychecklist)
            except Exception as msg:
                return Response({"message":"quality checklist id not found","errors":str(msg)},status=status.HTTP_400_BAD_REQUEST)
            for qualitycheckquestion in clientqualitychecklist.quality_question.all():
                response[qualitycheckquestion.id]={
                    "id":qualitycheckquestion.id,
                    "name":qualitycheckquestion.name,
                    "qualityid":qualitycheckquestion.questionid,
                    "activate":qualitycheckquestion.activate,
                    "created_date":qualitycheckquestion.created_date
                }
            return Response(response.values(),status=status.HTTP_200_OK)

        elif clientid is not None and client_quality_checklistid is  not None and projectid is not None and employeeid is not None:
            try:
                clientqualitychecklist=ClientQualityCheckList.objects.get(
                                                                        client_id=client,
                                                                        select_quality_checklist__qualityid=client_quality_checklistid,
                                                                        
                                                                        )
            except Exception as msg:
                return Response({"message":" client quality checklist id not found","errors":str(msg)},status=status.HTTP_400_BAD_REQUEST)
            
            try:
                Project.objects.get(
                    client_id=client,
                    projectId=projectid,
                    quality=clientqualitychecklist,
                    assigned_employee__employeeId=employeeid
                )
            except Exception as msg:
                return Response({"message":str(msg)})
            for qualitycheckquestion in clientqualitychecklist.quality_question.all():
                response[qualitycheckquestion.id]={
                    "id":qualitycheckquestion.id,
                    "name":qualitycheckquestion.name,
                    "qualityid":qualitycheckquestion.questionid,
                    "activate":qualitycheckquestion.activate,
                    "created_date":qualitycheckquestion.created_date
                }
            return Response(response.values(),status=status.HTTP_200_OK)

    def post(self,request):
        data=request.data
        qualitychecklists=data['qualitychecklist'].split(",")
        if not request.POST._mutable:
            request.POST._mutable = True 
        try:
            client=Client.objects.get(client_id=data['client_id'],client_status=True)#status=True,
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
        for qualitychecklist in qualitychecklists:
            try:
                getqualitychecklist=QualityCheckList.objects.get(Q(qualityid=qualitychecklist) 
                                            # & Q(status=True )   &
                                            # Q(activate=True)
                                            )
                # client.qualitychecklist.filter(id=getqualitychecklist.id)
                #client.qualitychecklist.add(getqualitychecklist)
                ClientQualityCheckList.objects.get_or_create(client_id=client,select_quality_checklist=getqualitychecklist)

            except Exception as msg:
                return Response({"message":qualitychecklist +" "+ "wrong quality check list id","required":str(msg)},status=status.HTTP_200_OK)
        
        return Response({"message":"quality check list added successful created"},status=status.HTTP_200_OK)
        

    def put(self,request):
        pass

    def patch(self,request):
        
        clientId=request.GET.get('client_id')
        clientchecklistid=request.GET.get('clientqualitycheklist_id')
        projects=request.GET.get('project_id')
        
        
        try:
            client=Client.objects.get(client_id=clientId)
        except Exception as msg:
            return Response({"message":"client id not found","required":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        try:
            clientchecklist=ClientQualityCheckList.objects.get(id=clientchecklistid,client_id=client)
        except Exception as msg:
            return Response({"message":str(msg)})

        
        for project in projects.split(","):
            try:
                getproject=client.project_set.get(projectId=project)
            except Exception as msg:
                return Response({"message":str(msg)})

            
            if getproject.quality.filter(id=clientchecklistid):
                #getproject.assigned_employee.remove(employee)
                pass
            else:
                getproject.quality.add(clientchecklist)
            
        return Response({"message":"project assigned updated","status":True},status=status.HTTP_200_OK) 
    
    
    def delete(self,request):
       
        qualitychecklists=request.GET.get('qualitychecklist')#record  id 1
        
        try:
            client=Client.objects.get(client_id=request.GET.get('client_id'),status=True,client_status=True)
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ClientQualityCheckList.objects.get(id=qualitychecklists,client_id=client).delete()
            return Response({"message":"quallity check list remove successful","status":True},status=status.HTTP_200_OK)
        except Exception as msg:
            return Response({"message":qualitychecklists +" "+ "wrong quality check list id","required":str(msg),"status":False},status=status.HTTP_200_OK)
        
        


"""ADD,GET,UPDATE,DELETE SEFTY CHECK LIST ASSING PROJECT"""
class Add_Sefty_CheakList(APIView):
    
    """GET SEFTY CHECK LIST"""
    def get(self,request):
        clientid=request.GET.get('client_id')
        seftyid=request.GET.get('safty_id')
        projectid=request.GET.get('project_id')
        employeeid=request.GET.get('employee_id')
    
        response={}
        try:
            client=Client.objects.get(client_id=clientid,status=True,client_status=True)
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
        
        
        if clientid is not None and  seftyid is None and projectid is None:
            for seftychecklist in client.clientseftychecklist_set.all():
                
                response[seftychecklist.id]={
                                        "id":seftychecklist.id,
                                        "name":seftychecklist.select_sefty_checklist.name,
                                        "saftychecklistid":seftychecklist.select_sefty_checklist.saftychecklistid,
                                        "status":seftychecklist.select_sefty_checklist.activate,
                                        "created_date":seftychecklist.created_date,
                                        "assign_project":[ 
                                            {
                                            "project_id":project.projectId,
                                            "project_name":project.project_name
                                            }
                                            for project in client.project_set.filter(sefty=seftychecklist)
                                             ]
                                        
                                            }
            return Response(response.values(),status=status.HTTP_200_OK)

        elif clientid is not  None and seftyid is not None and projectid is None:
            checkseftychecklist=client.seftychecklist.filter(saftychecklistid=seftyid)
            
            if checkseftychecklist.exists() :
                seftychecklist_question=ClientSeftyCheckList.objects.filter(
                                    Q(client_id__id=client.id) & 
                                    Q(select_sefty_checklist__saftychecklistid=seftyid) 
                                    
                                    )

            for seftyquestion in seftychecklist_question:
                response[seftyquestion.id]={
                    "id":seftyquestion.id,
                    "name":seftyquestion.name,
                    "questionid":seftyquestion.questionid,
                    "activate":seftyquestion.activate,
                    "created_date":seftyquestion.created_date
                    }
            return Response(response.values(),status=status.HTTP_200_OK)
        
        elif clientid is not  None and seftyid is not None and projectid is not None and employeeid is not None:
            
            try:
                seftychecklist_question=ClientSeftyCheckList.objects.get(
                                Q(client_id__id=client.id) & 
                                Q(select_sefty_checklist__saftychecklistid=seftyid) 
                                
                                )
            except Exception as msg:
                return Response({"message":"safty checklist not found","status":False},status=status.HTTP_400_BAD_REQUEST)
            try:
                Project.objects.get(
                    client_id=client,
                    projectId=projectid,
                    sefty=seftychecklist_question,
                    assigned_employee__employeeId=employeeid
                )
            except Exception as msg:
                return Response({"message":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
            for seftyquestion in seftychecklist_question.sefty_question.all():
                response[seftyquestion.id]={
                    "id":seftyquestion.id,
                    "name":seftyquestion.name,
                    "questionid":seftyquestion.questionid,
                    "activate":seftyquestion.activate,
                    "created_date":seftyquestion.created_date
                    }
            return Response(response.values(),status=status.HTTP_200_OK)  
    
    """ADD SEFTY CHECK LIST"""
    def post(self,request):
        data=request.data
        seftychecklists=data['seftychecklist'].split(",")
        if not request.POST._mutable:
            request.POST._mutable = True 
        try:
            client=Client.objects.get(client_id=data['client_id'],client_status=True)#,status=True
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
        for seftychecklist in seftychecklists:
            try:
                getseftychecklist=SeftyCheckList.objects.get(Q(saftychecklistid=seftychecklist) 
                                            # & Q(status=True )   &
                                            # Q(activate=True)
                                            )
                
                
                #client.seftychecklist.add(getseftychecklist)
                ClientSeftyCheckList.objects.get_or_create(client_id=client,select_sefty_checklist=getseftychecklist)
            except Exception as msg:
                return Response({"message":seftychecklist +" "+ "wrong sefty check list id","required":str(msg)},status=status.HTTP_200_OK)
        
        return Response({"message":"sefty check list added successful"},status=status.HTTP_200_OK) 
    def put(self,request):
        pass 
    
    def patch(self,request):
        
        clientId=request.GET.get('client_id')
        clientchecklistid=request.GET.get('clientsaftycheklist_id')
        projects=request.GET.get('project_id')
        
        
        try:
            client=Client.objects.get(client_id=clientId)
        except Exception as msg:
            return Response({"message":"client id not found","required":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        try:
            clientchecklist=ClientSeftyCheckList.objects.get(id=clientchecklistid,client_id=client)
        except Exception as msg:
            return Response({"message":str(msg)})

        
        for project in projects.split(","):
            try:
                getproject=client.project_set.get(projectId=project)
            except Exception as msg:
                return Response({"message":str(msg)})

            
            if getproject.quality.filter(id=clientchecklistid):
                #getproject.assigned_employee.remove(employee)
                pass
            else:
                getproject.sefty.add(clientchecklist)
            
        return Response({"message":"project assigned updated","status":True},status=status.HTTP_200_OK) 
    """pending status"""
    def delete(self,request):
        
        seftychecklists=request.GET.get('seftychecklist')
        
        try:
            client=Client.objects.get(client_id=request.GET.get('client_id'),status=True,client_status=True)
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
       
        try:
            ClientSeftyCheckList.objects.get(id=seftychecklists,client_id=client).delete()
            return Response({"message":"sefty check list deleted","status":True},status=status.HTTP_200_OK) 
        except Exception as msg:
            return Response({"message":seftychecklists +" "+ "wrong sefty check list id","required":str(msg)},status=status.HTTP_200_OK)
        
        


"""CHOOSE  AND ADD QUALITY CHECKLIST QUESTION BY CLIENT"""
class Client_Add_QualityChecklist_Question(APIView):
    def get(self,request):
        response={}
        clientID=request.GET.get('client_id')
        projectID=request.GET.get('project_id')
        clientchecklistid=request.GET.get('checklistid')#this is ClientQualityCheckList table id(1,2,3 not Qlt001)
        try:
            client=Client.objects.get(client_id=clientID,client_status=True)#,status=True
            clientqualitychecklist=ClientQualityCheckList.objects.get(
                                                                    Q(client_id=client,id=clientchecklistid ) 
                                                                    |
                                                                    Q(client_id=client,select_quality_checklist__qualityid=clientchecklistid ) 
                                                                    
                                                                    )
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg)},status=status.HTTP_400_BAD_REQUEST)
        questions=clientqualitychecklist.quality_question.all()
        if clientID is not None and projectID is None:
            
            
            print(questions)
            for que in questions :
                response[que.id]={
                    
                    "name":que.name,
                    "questionid":que.questionid,
                    "status":que.status


                }
                
            return Response(response.values(),status=status.HTTP_200_OK)
        elif clientID is not None and projectID is not None:
            try:
                Project.objects.get(client_id=client,projectId=projectID,quality=clientqualitychecklist)
            except Exception as msg:
                return Response({"message":"client qualitychecklist not add in this project yet!",
                "error":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

            
            for que in questions :
                response[que.id]={
                    "id":que.id,
                    "name":que.name,
                    "questionid":que.questionid,
                    "status":que.status


                }
                
            return Response(response.values(),status=status.HTTP_200_OK)
        else:
            return Response({"message":"key is wrong","status":False})




    def post(self,request):
        data=request.data
        qualityquestionids=data['qualityquestion'].split(",")#QLTQ.0001
        qualitychecklistid=data['qualitychecklist']
        if not request.POST._mutable:
            request.POST._mutable = True 
        try:
            client=Client.objects.get(client_id=data['client_id'],client_status=True)#,status=True
            qualitychecklist=QualityCheckList.objects.get(qualityid=qualitychecklistid)
            clientqualitychecklist=ClientQualityCheckList.objects.get(client_id=client,select_quality_checklist=qualitychecklist)
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg)},status=status.HTTP_400_BAD_REQUEST)
        for qualityquestionid in qualityquestionids:
            try:
                getqualitychecklist=QualityQuestion.objects.get(Q(questionid=qualityquestionid) 
                                            # & Q(status=True )   &
                                            # Q(activate=True)
                                            )
               

                clientqualitychecklist.quality_question.add(getqualitychecklist)
            except Exception as msg:
                return Response({"message":qualityquestionid +" "+ "wrong qualitycheck list question  id","required":str(msg)},status=status.HTTP_200_OK)
        
        return Response({"message":"quallity check list added successful created"},status=status.HTTP_200_OK) 
    
    def delete(self,request):
        data=request.data
        qualityquestionids=data['qualityquestion'].split(",")#QLTQ.0001
       
        try:
            client=Client.objects.get(client_id=data['client_id'],status=True,client_status=True)
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
        for qualityquestionid in qualityquestionids:
            try:
                getqualitychecklist=QualityQuestion.objects.get(Q(questionid=qualityquestionid) 
                                            # & Q(status=True )   &
                                            # Q(activate=True)
                                            )
                # client.qualitychecklist.filter(id=getqualitychecklist.id)
                client.qualityquestion.remove(getqualitychecklist)
            except Exception as msg:
                return Response({"message":qualityquestionid +" "+ "wrong qualitycheck list question  id","required":str(msg)},status=status.HTTP_200_OK)
        
        return Response({"message":"quallity check list remove successful created"},status=status.HTTP_200_OK)


"""CHOOSE  AND ADD SEFTY CHECKLIST QUESTION BY CLIENT"""
class Client_Add_SeftyChecklist_Question(APIView):
    def get(self,request):
        response={}
        clientID=request.GET.get('client_id')
        projectID=request.GET.get('project_id')
        clientchecklistid=request.GET.get('checklistid')#this is ClientQualityCheckList table id(1,2,3 not Qlt001)
        try:
            client=Client.objects.get(client_id=clientID,client_status=True)#,status=True
            clientsaftychecklist=ClientSeftyCheckList.objects.get(client_id=client,id=clientchecklistid)
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg)},status=status.HTTP_400_BAD_REQUEST)
        
        saftychecklistquestion=clientsaftychecklist.sefty_question.all()
        
        if clientID is not None and projectID is None:

            for que in saftychecklistquestion:
                response[que.id]={
                    
                    "name":que.name,
                    "questionid":que.questionid,
                    "status":que.status


                }
            return Response(response.values(),status=status.HTTP_200_OK) 
        elif clientID is not None and projectID is not None:
            try:
                Project.objects.get(client_id=client,projectId=projectID,sefty=clientsaftychecklist)
            except Exception as msg:
                return Response({"message":"client qualitychecklist not add in this project yet!",
                    "error":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
            for que in saftychecklistquestion:
                    response[que.id]={
                        'id':que.id,
                        "name":que.name,
                        "questionid":que.questionid,
                        "status":que.status


                    }
                
            return Response(response.values(),status=status.HTTP_200_OK) 
        else:
            return Response({"message":"some key is missing","status":False},status=status.HTTP_400_BAD_REQUEST)
    def post(self,request):
        data=request.data
        seftyquestions=data.get('seftyquestion').split(",")
        seftychecklistid=data['seftychecklist']
        if not request.POST._mutable:
            request.POST._mutable = True 
        try:
            client=Client.objects.get(client_id=data['client_id'],client_status=True)#,status=True
            seftychecklist=SeftyCheckList.objects.get(saftychecklistid=seftychecklistid)
            clientseftychecklist=ClientSeftyCheckList.objects.get(client_id=client,select_sefty_checklist=seftychecklist)
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg)},status=status.HTTP_400_BAD_REQUEST)
        
        if len(seftyquestions)==0:
            saftyquestion=seftychecklist.seftyquestion_set.all()
            seftyquestions=[ question.questionid for question in saftyquestion]
        else:
            seftyquestions
        
        for seftyquestion in seftyquestions:
            try:
                getseftyquestion=SeftyQuestion.objects.get(Q(questionid=seftyquestion) 
                                            # & Q(status=True )   &
                                            # Q(activate=True)
                                            )
                # client.qualitychecklist.filter(id=getqualitychecklist.id)
                clientseftychecklist.sefty_question.add(getseftyquestion)
            except Exception as msg:
                return Response({"message":seftyquestion +" "+ "wrong sefty check list id","required":str(msg)},status=status.HTTP_200_OK)
        return Response({"message":"sefty check list added successful created"},status=status.HTTP_200_OK)
   
    def delete(self,request):
        data=request.data
        seftyquestions=data['seftyquestion'].split(",")
        try:
            client=Client.objects.get(client_id=data['client_id'],status=True,client_status=True)
        except Exception as msg:
            return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
        for seftyquestionid in seftyquestions:
            try:
                getseftyquestion=SeftyQuestion.objects.get(Q(questionid=seftyquestionid) 
                                            # & Q(status=True )   &
                                            # Q(activate=True)
                                            )
                # client.qualitychecklist.filter(id=getqualitychecklist.id)
                client.seftychecklist.remove(getseftyquestion)
            except Exception as msg:
                return Response({"message":seftyquestionid +" "+ "wrong sefty check list id","required":str(msg)},status=status.HTTP_200_OK)
        return Response({"message":"seftychecklist question removed form your list"},status=status.HTTP_200_OK)
        



class Being_Inspected_Area_Details(APIView):
    def get(self,request):
        projectid=request.GET.get('project_id')
        client=request.GET.get('client_id')
        Inspectionid=request.GET.get('inspection_id')
       
        res={}
        try:
            client=Client.objects.get(client_id=client,client_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        try:
            project=Project.objects.get(client_id=client,projectId=projectid, project_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"project id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        if Inspectionid:
            query=Q(id=Inspectionid)
        else:
            query=Q(project=project)
        inspectionDeatails=InspectionDetail.objects.filter(query)
        if inspectionDeatails.exists():
            for insp in inspectionDeatails:
                res[insp.id]={
                    "id":insp.id,
                    "project_name":insp.project.project_name,
                    "projectId":insp.project.projectId,
                    "area_inspected":insp.area_inspected,
                    "material_name":insp.material_inspected.material_name,
                    "materialId":insp.material_inspected.materialId,
                    "area_inspected":insp.area_inspected,
                    "material_quantity":insp.material_quantity,
                    "material_unit":insp.material_unit,
                    "vendor_name":insp.vendor.vendor_name,
                    "vendorId":insp.vendor.vendorId,
                    "status":insp.status,
                    "employeeId":insp.employee,
                    "employee_name":get_object_or_404(Employee,employeeId=insp.employee).employee_name if insp.employee!=None else None,
                    #"approverid":project.objects.filter(approverid=insp.employee).exists() if insp.employee!=None else False,
                }
            return Response(res.values())
        else:
            return Response({"message":"no any inspection area posted yet","status":False},status=status.HTTP_400_BAD_REQUEST)
    def post(self,request):
        projectid=request.GET.get('project_id')
        client=request.GET.get('client_id')
        vendor=request.GET.get('vendor_id')
        material=request.GET.get('material_id')
        employeeid=request.data.get('employee_id')#EMP00001
        data=request.data
        try:
            client=Client.objects.get(client_id=client,client_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        try:
            project=Project.objects.get(client_id=client,projectId=projectid, project_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"project id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        projectmaterial=project.assigned_material.filter(materialId=material)
        projectvendor=project.vendor.filter(vendorId=vendor)
        projectemployee=project.assigned_employee.filter(employeeId=employeeid)
        if projectvendor.exists() and projectmaterial.exists() and projectemployee.exists() :
            try:
                insp=InspectionDetail.objects.create(
                        project=project,
                        area_inspected=data['area_inspected'],
                        material_inspected=projectmaterial[0],
                        material_quantity=data['material_quantity'],
                        material_unit=data['material_unit'],
                        vendor=projectvendor[0],
                        employee=employeeid
                )
                return Response({"message":"inspection Detail submited successful","inspection_id":insp.id,"status":True},status=status.HTTP_200_OK)
            except Exception as msg:
        
        
                return Response({"message":"all required field","error":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        elif projectmaterial.exists()==False:
            return Response({"message":"material id not exists","status":False},status=status.HTTP_400_BAD_REQUEST)
        
        elif projectvendor.exists()==False:
            return Response({"message":"vendor id not exists","status":False},status=status.HTTP_400_BAD_REQUEST)
        
        elif projectemployee.exists()==False:
            return Response({"message":"this employee id not exists in this project.contact with client","status":False},status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"message":"vendor id not exists","status":False},status=status.HTTP_400_BAD_REQUEST)



class SubmissionOf_Inspected_Area_Details(APIView):
    def get(self,request):
        
        projectid=request.GET.get('project_id')
        client=request.GET.get('client_id')
        Inspectionid=request.GET.get('inspection_id')
       
        res={}
        
        try:
            project=Project.objects.get(projectId=projectid, project_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"project id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        try:
            Client.objects.get(id=project.client_id.id,client_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        inspectionid=InspectionDetail.objects.get(id=Inspectionid,project=project)
        inspectionDeatails=inspectionid.inspectareaquestion_set.all()
        
        for insp in inspectionDeatails:
            serializer=InspectAreaQuestionserializers(insp,many=False).data

            res[insp.id]=serializer
            
        return Response(res.values())
    
    def post(self,request):
        postdata=request.data.get('data')

        for i in postdata:
            try:
                client=Client.objects.get(client_id=i['client_id'],client_status=True)#,status=True
                
            except Exception as msg:
                return Response({"message":"client id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

            try:
                project=Project.objects.get(client_id=client,projectId=i["project_id"], project_status=True)#,status=True
                
            except Exception as msg:
                return Response({"message":"project id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

            try:
                Inspection=InspectionDetail.objects.get(project=project,id=i["inspection_id"])
                
            except Exception as msg:
                return Response({"message":"InspectionDetail id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
            
            getinfo=InspectAreaQuestion.objects.filter(inspection=Inspection,
                                                        project=project,
                                                        client_id=client,
                                                        question=get_object_or_404(QualityQuestion,questionid=i['question_id']),
                                                        )
            # if getinfo.exists():
            #     return Response({"message":"question allready submited","status":getinfo.exists(),"questionid":i['question_id']},status=status.HTTP_200_OK)

            print(postdata)
            if project.quality.filter(quality_question__questionid=i['question_id']).exists(): 
        
                if i['complite_status']==False:
                    try:
                        insp,_=InspectAreaQuestion.objects.get_or_create(
                                inspection=Inspection,
                                project=project,
                                client_id=client,
                                question=get_object_or_404(QualityQuestion,questionid=i['question_id']),
                                complite_status=i['complite_status'],#True,False
                                not_complite_resion=i['not_complite_resion']

                        )
                    except Exception as msg:
                        return Response({"message":"all required field","error":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
                elif i['complite_status']==True :

                    try:
                        insp,_=InspectAreaQuestion.objects.get_or_create(
                                inspection=Inspection,
                                project=project,
                                client_id=client,
                                question=get_object_or_404(QualityQuestion,questionid=i['question_id']),
                                complite_status=i['complite_status'],#True,False
                                
                        )
                    except Exception as msg:
                
                        return Response({"message":"all required field","error":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message":"qualitychecklist question id not exists","questionid":i["question_id"],"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        complitestatus=Inspection.inspectareaquestion_set.filter(complite_status=False)
        if complitestatus.exists():
            return Response({"message":"need to reschedule remaining question",
                            # "inspection_area_id":insp.id,
                            "status":False,"number_of_reschedule_inspect":len(complitestatus)},status=status.HTTP_200_OK)
        else:
            return Response({"message":"inspection area Detail submited successful",
                           # "inspection_area_id":insp.id,
                            "number_of_reschedule_inspect":len(complitestatus),
                            "status":True},status=status.HTTP_200_OK)
    
    
    def put(self,request):
        
        inspectinsubmitid=request.GET.get('id')
        insp=get_object_or_404(InspectAreaQuestion,id=inspectinsubmitid)
        serializer=InspectAreaQuestionserializers(insp,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"updated success"})
        else:
            return Response(serializer.errors)

    def delete(self,request):
        inspectinsubmitid=request.GET.get('id')
        get_object_or_404(InspectAreaQuestion,id=inspectinsubmitid).delete()
        return Response({"message":"inspection area deleted","status":True})
        
        

class SubmissionOf_Inspected_Area_image(APIView):
    def get(self,request):
        pass

    def post(self,request):
        Inspectionid=request.data.get('inspection_id')
        projectid=request.data.get('project_id')
        clientId=request.data.get('client_id')
       
        data=request.data
        try:
            client=Client.objects.get(client_id=clientId,client_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        try:
            project=Project.objects.get(client_id=client,projectId=projectid, project_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"project id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        try:
            Inspection=InspectionDetail.objects.get(project=project,id=Inspectionid)
            
        except Exception as msg:
            return Response({"message":"InspectionDetail id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        
        
        uploadfile=data['image']
        print("=====upload single image====")
        
        
        
        format, imgstr = uploadfile.split(';base64,')
        ext = format.split('/')[-1]
        uploadfile = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        #print(uploadfile)
        print("=====base64 change image====")
        
        try:
            InspectAreaQuestionimage.objects.create(
                    inspection=Inspection,
                    project=project,
                    client_id=client,
                    #image=request.FILES.getlist('image')[0]
                    image=uploadfile
            )
            print("try block")
            
        except Exception as msg:
            return Response({"message":"all required field","error":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        inspection_image=Inspection.inspectareaquestionimage_set.all()
        response={
            "image":[{"id":img.id,"image":img.image.url if img.image else None} for img in inspection_image] 
        }   
        
        return Response(response,status=status.HTTP_200_OK)

"""this checklist to reschedule and revisit again"""                 
class ListOfFailedCheckList(APIView):
    def get(self,request):
        client=request.GET.get('client_id')
        inspectid=request.GET.get("inspectid")
        typeofchecklist=request.GET.get('type')
        projectid=request.GET.get('projectid')
        
        response={}
        if client is not None:
            project=InspectionDetail.objects.filter(project__client_id__client_id=client)
            for i in project:
                detail=InspectAreaQuestion.objects.filter(inspection__id=i.id,complite_status=False)
                response[i.id]={
                    "id":i.id,
                    "project_name":i.project.project_name,
                    "projectID":i.project.projectId,
                    "project_id":i.project.id,
                    "datail":[ {
                        "checklist":i.question.quality.name,
                        "qualityid":i.question.quality.qualityid,
                        "inspectid":i.inspection.id,
                        }  for i in detail],
                    
                    "pendinginspect":detail.count()
                }
            return Response(response.values())

        elif inspectid is not None:
            try:
                inspect= InspectionDetail.objects.get(id=inspectid)
            except Exception as e:
                return Response({"message":str(e),"errors":"Inspectid invalid"})
            complitestatus=inspect.inspectareaquestion_set.filter(complite_status=False).order_by("-id")
            serializer=InspectAreaQuestionserializers(complitestatus,many=True)
            return Response(serializer.data)
        
        elif typeofchecklist=="qualitychecklist" and projectid is not None:
            detail=InspectAreaQuestion.objects.filter(project__projectId=projectid,complite_status=False)
            for i in detail:
                response[i.question.quality.qualityid]={
                    "checklist":i.question.quality.name,
                    "qualityid":i.question.quality.qualityid,
                    "projectId":i.project.projectId,
                    "inspectid":i.inspection.id
                }
            return Response(response.values())
        else:
            return Response({"message":"wrong request"})



"""Reschedule date for inspection"""  
import datetime
class RescheduleDateForInspection(APIView):

    def get(self,request):
        
        checklistid=request.GET.get('checklistid')
        projectid=request.GET.get('projectid')
        response={}
       
        try:
            project=Project.objects.get(projectId=projectid)
            QualityCheckList.objects.get(qualityid=checklistid)
        except Exception as e:
            return Response({"message":str(e)})
        inspectionQuestion=InspectAreaQuestion.objects.filter(
                                    Q(project__projectId=project.projectId)
                                    &
                                    Q(question__quality__qualityid=checklistid)
                                    &
                                    Q(complite_status=False)
                             ).order_by('-id')
            


            
    

        # return Response({"message":inspectionQuestion.exists()})
        for  i in inspectionQuestion:
            reschedule=RescheduleInspect.objects.filter(inspection__id=i.inspection.id).order_by('-id')
            for j in reschedule:
                serializer=Rescheduleserializers(j,many=False).data
                
                serializer['inspectionid']=j.inspection.id
                serializer["checklist"]=i.question.quality.name
                serializer["question"]=i.question.name
                serializer["projectId"]=i.project.projectId
                response[j.id]=serializer
        
        return Response(response.values())
        
        
        



    def post(self,request):

        if not request.POST._mutable:
            request.POST._mutable = True
        data=request.data
        inspectid=request.GET.get("inspectid")
        try:
           inspect= InspectionDetail.objects.get(id=inspectid)
           client=Client.objects.get(client_id=request.GET.get('client_id'),client_status=True)
        except Exception as e:
            return Response({"message":str(e)})
        
        
        data["client_id"]=client.id
        data['inspection']=inspect.id
        
        serializer=RescheduleInspectserializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        
    def put(self,request):
        if not request.POST._mutable:
            request.POST._mutable = True
        data=request.data
        inspectid=request.GET.get("inspect_id")
        rescheduleid=request.GET.get("reschedule_id")
        try:
           inspect= InspectionDetail.objects.get(id=inspectid)
           client=Client.objects.get(client_id=request.GET.get('client_id'),client_status=True)
        except Exception as e:
            return Response({"message":str(e)})
        
        
        data["client_id"]=client.id
        data['inspection']=inspect.id
        try:
            reschedule=RescheduleInspect.objects.get(id=rescheduleid)
        except Exception as e:
            return Response({"message":"Reschedule id invalid","status":False,"error":str(e)})
        serializer=RescheduleInspectserializers(reschedule,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            inspect.update_date=datetime.datetime.now()
            inspect.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)




"""ONLY FOR APPROVER SHOW LIST OF INSPECTION"""                 
class ListOfInspection(APIView):
    def get(self,request):
        client=request.GET.get('client_id')
        projectid=request.GET.get('projectid')
        
        response={}
        if client is not None and projectid is not None:
            try:
                project=Project.objects.get(client_id__client_id=client,projectId=projectid)
            except Exception as e:
                return Response({"message":str(e),"error":"project id and clint id not found","status":False})

            inspectionid=InspectionDetail.objects.select_related("project").filter(project__client_id__client_id=client)
            if inspectionid.exists()==False:
                return Response({"message":"Inspection List Not found"})
            for inspection in inspectionid:
               
                inspectquestion=InspectAreaQuestion.objects.filter(inspection=inspection,complite_status=False)
                if inspectquestion.exists()==False:
                    instpection_complite=InspectAreaQuestion.objects.filter(inspection=inspection)
                    if instpection_complite.exists():
                        response[inspection.id]={
                            "inspectionid":inspection.id,
                            "project_name":inspection.project.project_name,
                            "projectId":inspection.project.projectId,
                            "employee":inspection.employee if inspection.employee else None,
                            "checklist":instpection_complite[0].question.quality.name,
                            "question_count":instpection_complite.count()   
                        }
                    else:
                        pass
            return Response(response.values())

        
        else:
            return Response({"message":"wrong data input","status":False})


"""Individual approval inspection detail"""
class IndividualInspection(APIView):
    def get(self,request):
        inspectionid=request.GET.get('inspection_id')
       
        try:
            inspection=InspectionDetail.objects.get(id=inspectionid)
        except Exception as e:
            return Response({"message":str(e),"status":False})
        inspectionquestion=InspectAreaQuestion.objects.filter(inspection=inspection)
        emloyee=Employee.objects.get(employeeId=inspection.employee)
        inspection_image=inspection.inspectareaquestionimage_set.all()
        serializer=InspectionDetailserializers(inspection,many=False).data
        serializer["project_name"]=inspection.project.project_name
        serializer["projectId"]=inspection.project.project_name
        serializer["material_inspected_name"]=inspection.material_inspected.material_name
        serializer["vendor"]=inspection.vendor.vendor_name
        serializer["employee"]=inspection.employee
        serializer["question_count"]=inspectionquestion.count()

        serializer["question"]=[
            { "question":question.question.quality.name,
             "complite_staus":question.complite_status}
             for question in inspectionquestion

                ]
        
        serializer["inspection_image"]=[
            { "id":img.id,
             "image":img.image.url if img.image else None}
             for img in inspection_image

                ]
        serializer['number_of_image']=len(inspection_image)
        serializer['city']=inspection.project.city
        
        serializer['employee_name']=emloyee.employee_name
            
        return Response(serializer,status=200)
    
    def put(self,request):
        if not request.POST._mutable:
            request.POST._mutable=True
        inspectionid=request.GET.get('inspection_id')
        data=request.data
       
        try:
            inspection=InspectionDetail.objects.get(id=inspectionid)
        except Exception as e:
            return Response({"message":str(e),"status":False})

        serializers=InspectionDetailserializers(inspection,data=data,partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response({"message":"Approver status updated successfully","status":True})
        else:
            return Response(serializers.errror,status=404)

class ReportUpload(APIView):
    def get(self,request):
        Inspectionid=request.GET.get('inspection_id')
        clientId=request.GET.get('client_id')
        for c in Client.objects.all():
            print(c.client_id)
        
        try:
            client=Client.objects.get(client_id=clientId,client_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        try:
            Inspection=InspectionDetail.objects.get(id=int(Inspectionid))
            
        except Exception as msg:
            return Response({"message":"InspectionDetail id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        inspection_doc=Inspection.reportdoc_set.all()
        response={
            "image":[{"id":doc.id,"image":doc.document.url if doc.document else None} for doc in inspection_doc] 
        }   
        
        return Response(response,status=status.HTTP_200_OK)
        
    
    
    
    def post(self,request):
        Inspectionid=request.GET.get('inspection_id')
        clientId=request.GET.get('client_id')
        data=request.data
        try:
            client=Client.objects.get(client_id=clientId,client_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        try:
            Inspection=InspectionDetail.objects.get(id=int(Inspectionid))
            
        except Exception as msg:
            return Response({"message":"InspectionDetail id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        
        try:
            ReportDoc.objects.create(
                    inspection=Inspection,
                    client_id=client,
                    document=request.FILES['document']
            )
            
        except Exception as msg:
            return Response({"message":"all required field","error":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        inspection_doc=Inspection.reportdoc_set.all()
        response={
            "image":[{"id":doc.id,"image":doc.document.url if doc.document else None} for doc in inspection_doc] 
        }   
        
        return Response(response,status=status.HTTP_200_OK)
    



# from django.core.mail import EmailMessage
# email = EmailMessage('Subject', 'Body', to=['your@email.com'])
# email.send()
# from django.core.mail import EmailMessage
# email = EmailMessage('Subject', 'Body', to=['def@domain.com'])
# email.send()
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
from django.conf import settings
from django.core.mail import send_mail
class SendEmail(APIView):
    def get(self,request):
        subject="testing mail"
        message="finaly send this email"
        senderemail = settings.EMAIL_HOST_USER
        receiveremail='rakeshsinha8292@gmail.com'
        try:
            send_mail(subject, message, senderemail, [receiveremail])
            return Response({"mes":"ok"})
        except Exception as meg:
            return Response({"mes":str(meg)})
# from django.core.mail import send_mail
# send_mail('subject','message','sender email',['receipient email'],    fail_silently=False)

class SendOpt(APIView):

    def get(self,request,format=None):
        
        generated_otp = random.randint(100000,999999)
        phone=request.GET.get('phone_number')
        if phone is not None:
            try:
                Employee.objects.get(phone_number=phone,employee_status=True)
            except Exception as msg:
                return Response({"message":"This phone number not register","status":False},status=status.HTTP_400_BAD_REQUEST)

            try:
                saveotp=SaveOtp.objects.get(contact=phone)
                sending_otp(saveotp.otp,phone)
            except Exception as msg:
                SaveOtp.objects.create(contact=phone,otp=generated_otp)
                sending_otp(generated_otp,phone)
                pass
        
            return Response({'status':True,
                            "phone":phone,
                            'message':"Otp sented Successful"},status=status.HTTP_202_ACCEPTED)
        else:
            return Response({"message":"key is missing ","status":False},status=status.HTTP_400_BAD_REQUEST)

class OtpVerificaton(APIView):
   def get(self,request):
        otp=request.GET.get('otp')
        phone=request.GET.get('phone_number')
        try:
            employee=Employee.objects.get(phone_number=phone,employee_status=True)
        except Exception as msg:
            return Response({"message":"this phone employee is not activate yet!","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            get_otp=SaveOtp.objects.get(contact=phone,otp=otp)
        except Exception as msg:
            return Response({"message":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
            
        if otp is not None :
            
            if int(otp) == get_otp.otp:
                get_otp.delete()
                projects=Project.objects.filter(client_id=employee.client_id,assigned_employee=employee,project_status=True)
                seializer=Employeeserializers(employee,many=False).data
                seializer.update({
                    "client_id":employee.client_id.client_id,
                    "client_name":employee.client_id.client_name,
                    "assigned_license":employee.assigned_license.license_id,
                    # "projects":[{
                    #     "projectId":project.projectId,
                    #     "project_name":project.project_name,
                    #     "city":project.city,
                    #     "approver":project.approver,
                    #     "approverid":project.approverid,
                    #     "project_status":project.project_status
                        

                    # } for project in projects]  
                     })
                return Response(seializer,status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"message":"otp is invalid","status":False},status=400)
              
        else:
            return Response({"message":"key is missing ","status":False},status=status.HTTP_400_BAD_REQUEST)


"""Site Observation Report"""
class SiteObservationReportGenerate(APIView):
    
        
    def get(self,request):
        site_observation_id=request.GET.get('siteobsevationid')
        project_id=request.GET.get('project_id')
        project=request.GET.get('project')
        
        response={}
        if site_observation_id is not None:
            query=Q(siteobsevationid__exact=site_observation_id)
        
        elif project_id is not None: 
            query=Q(project__projectId=project_id)      
        else:
            query=Q( 
                    Q(project__projectId=project)
                    &
                    Q(observatation_status=False)
                    
                    )
        
       
        obsevationreports=SiteObservationReport.objects.filter(query).order_by('-id')
        for obsevationid in obsevationreports:
            serializer=SiteObservationGetserializers(obsevationid,many=False).data 

            serializer['image']=[ 
                                {"id":img.id,'image':img.image.url if img.image else None,
                                "siteobsevationid":img.site_image_id
                                } 
                                for img in ObservationReportImage.objects.filter(site_image_id=obsevationid.siteobsevationid)
                                ]
            serializer['contractor']=obsevationid.vendorId.vendor_name 
            serializer['contractorid']=obsevationid.vendorId.id
            serializer['vendorid']=obsevationid.vendorId.vendorId
            response[obsevationid.id]=serializer 
            if site_observation_id is not None:
                return Response(serializer,status=200)
        return Response(response.values(),status=200)
    
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable=True
        projectid=request.GET['project_id']
        clientId=request.GET['client_id']
        data=request.data
        

        
        try:
            client=Client.objects.get(client_id=clientId,client_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        try:
            project=Project.objects.get(client_id__id=client.id ,projectId=projectid)
            
        except Exception as msg:
            return Response({"message":"Project  id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        vendors=project.vendor.filter(vendorId=data['vendorId']) 
        if vendors.exists()==False:
            return Response({"message":"Vendor id not found","status":False},status=400)
        
        
        this_image=ObservationReportImage.objects.filter(site_image_id__exact=data['site_image_id'])
        if this_image.exists()==False:
            return Response ({"message":"Enter site image id invalid","status":False},status=200)
        
        data['client_id']=client.id
        data['project']=project.id
        data['vendorId']=vendors[0].id
        data['siteobsevationid']=this_image[0].site_image_id

        serializer=SiteObservationReportserializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)  
        else:
            return Response(serializer.errors,status=400)    
        
    def put(self,request):
        
        if not request.POST._mutable:
            request.POST._mutable=True
        
        site_observation_id=request.GET['siteobsevationid']
        data=request.data
        try:
            obsevationid=SiteObservationReport.objects.get(siteobsevationid=site_observation_id)
        except Exception as e:
            return Response({"message":"obsevation id not found","staus":False},status=400)
        
        data['client_id']=obsevationid.client_id.id
        data['project']=obsevationid.project.id
        data['vendorId']=obsevationid.vendorId.id
        data["siteobsevationid"]=obsevationid.siteobsevationid
        serializer=SiteObservationGetserializers(obsevationid,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        else:
            return Response(serializers.error,status=400) 
       
    
class SiteObservationImage(APIView):
    
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable=True
        data=request.data
        site_observation_id=request.GET['site_image_id']
        
        uploadfile=data['image']
        format, imgstr = uploadfile.split(';base64,')
        ext = format.split('/')[-1]
        uploadfile = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        this_image=ObservationReportImage.objects.filter(site_image_id__exact=site_observation_id)
        if this_image.exists():
            obj=ObservationReportImage.objects.create(image=uploadfile,site_image_id=site_observation_id)
            images=ObservationReportImage.objects.filter(site_image_id__exact=site_observation_id)
            return Response({"message":"image uploaded successfully",
                             "status":True,
                             "site_image_id":site_observation_id,
                             'image':[{
                                 "id":image.id,
                                 "image":image.image.url if image.image else None,
                                 "site_image_id":image.site_image_id
                             }
                                 
                                 for image in images
                             ]
                             
                             },status=200) 
        else:
            obj=ObservationReportImage.objects.create(image=uploadfile)
            return Response({"message":"image uploaded successfully",
                             "status":True,"site_image_id":obj.site_image_id},status=200)
        
    def put(self,request):
        if not request.POST._mutable:
            request.POST._mutable=True
            
        data=request.data
        site_observation_id=request.GET['imagid']
        try:
            obsevationid=ObservationReportImage.objects.get(id=site_observation_id)
        except Exception as e:
            return Response({"message":"obsevation id not found","staus":False},status=400)
        
        uploadfile=data['image']
        format, imgstr = uploadfile.split(';base64,')
        ext = format.split('/')[-1]
        uploadfile = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        #print(uploadfile)
        print("=====base64 change image====")
        try:
            obsevationid.image=uploadfile
            obsevationid.save()
            return Response({"message":"image uploaded update successfully","status":True},status=200) 
        except Exception as e:
            return Response({"message":str(e),"status":False},status=400)
        


"""Non Compliance Report"""
class NcrGenerate(APIView):
    
        
    def get(self,request):
        site_observation_id=request.GET.get('ncrid')
        project_id=request.GET.get('project')
        
        
        response={}
        if site_observation_id is not None:
            query=Q(ncrid__exact=site_observation_id)
        
        elif project_id is not None: 
            query=Q(project__projectId=project_id)      
        else:
            query=Q( 
                    Q(project__projectId=project_id)
                    &
                    Q(ncr_status=True)
                    
                    )
        
       
        obsevationreports=NonComplianceReport.objects.filter(query).order_by('-id')
        for obsevationid in obsevationreports:
            serializer=NCRGetserializers(obsevationid,many=False).data 

            serializer['image']=[ 
                                {"id":img.id,'image':img.image.url if img.image else None,
                                "ncrid":obsevationid.ncrid
                                } 
                                for img in NonComplianceReportImage.objects.filter(ncr_image_id__exact=obsevationid.ncrid)
                                ]
            serializer['contractor']=obsevationid.vendorId.vendor_name 
            serializer['contractorid']=obsevationid.vendorId.id
            serializer['vendorid']=obsevationid.vendorId.vendorId
            response[obsevationid.id]=serializer 
            if site_observation_id is not None:
                return Response(serializer,status=200)
        return Response(response.values(),status=200)
    
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable=True
        projectid=request.GET['project_id']
        clientId=request.GET['client_id']
        data=request.data
        
     
        try:
            client=Client.objects.get(client_id=clientId,client_status=True)#,status=True
            
        except Exception as msg:
            return Response({"message":"client id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)

        try:
            project=Project.objects.get(client_id__id=client.id ,projectId=projectid)
            
        except Exception as msg:
            return Response({"message":"Project  id not found","errors":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        
        vendors=project.vendor.filter(vendorId=data['vendorId']) 
        if vendors.exists()==False:
            return Response({"message":"Vendor id not found","status":False},status=400)
        #uuid_id=uuid.uuid4()
        this_image=NonComplianceReportImage.objects.filter(ncr_image_id__exact=data['ncr_image_id'])
        if this_image.exists()==False:
            return  Response({"message":"Enter ncr_image_id is not valid","status":False},status=200)
        data['client_id']=client.id
        data['project']=project.id
        data['vendorId']=vendors[0].id
        data['ncrid']=data['ncr_image_id']
        serializer=NCRserializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200) 
           
            
            
        else:
            return Response(serializer.errors,status=400)    
        
    def put(self,request):
        
        if not request.POST._mutable:
            request.POST._mutable=True
        
        site_observation_id=request.GET['ncrid']
        data=request.data
        try:
            obsevationid=NonComplianceReport.objects.get(ncrid=site_observation_id)
        except Exception as e:
            return Response({"message":"NCR id not found","staus":False},status=400)
        
        data['client_id']=obsevationid.client_id.id
        data['project']=obsevationid.project.id
        data['vendorId']=obsevationid.vendorId.id
        data["ncrid"]=obsevationid.ncrid
        serializer=NCRGetserializers(obsevationid,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        else:
            return Response(serializers.error,status=400) 
       
    
class NCRImage(APIView):
    
    def post(self,request):
        if not request.POST._mutable:
            request.POST._mutable=True
        data=request.data
        ncr_id=request.GET['ncr_image_id']
        site=NonComplianceReportImage.objects.filter(ncr_image_id__exact=ncr_id)
        
        uploadfile=data['image']
        format, imgstr = uploadfile.split(';base64,')
        ext = format.split('/')[-1]
        uploadfile = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
       
        print("=====base64 change image====")
        
        if site.exists():
            obj=NonComplianceReportImage.objects.create(image=uploadfile,ncr_image_id=ncr_id)
            return Response({"message":"image uploaded successfully",
                            "status":True,"ncr_image_id":ncr_id},status=200)
        else:
            obj=NonComplianceReportImage.objects.create(image=uploadfile)
            return Response({"message":"image uploaded successfully",
                            "status":True,"ncr_image_id":obj.ncr_image_id},status=200) 
        
        
    def put(self,request):
        if not request.POST._mutable:
            request.POST._mutable=True
            
        data=request.data
        site_observation_id=request.GET['imagid']
        try:
            obsevationid=NonComplianceReportImage.objects.get(id=site_observation_id)
        except Exception as e:
            return Response({"message":"obsevation id not found","staus":False},status=400)
        
        uploadfile=data['image']
        format, imgstr = uploadfile.split(';base64,')
        ext = format.split('/')[-1]
        uploadfile = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        #print(uploadfile)
        print("=====base64 change image====")
        try:
            obsevationid.image=uploadfile
            obsevationid.save()
            return Response({"message":"image uploaded update successfully","status":True},status=200) 
        except Exception as e:
            return Response({"message":str(e),"status":False},status=400)        