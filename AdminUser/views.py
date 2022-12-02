from functools import partial
from operator import index
from django.http import response
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from AdminUser.globleId import qualityquestionid,seftyquestionid,seftycheacklist,qualitycheacklist
from AdminUser.models import QualityCheckList, SeftyCheckList
from AdminUser.serializers import *
from account.models import *
from rest_framework import status
from account.serializers import *
from account.client import generate_client_id,license_generate
from datetime import date,time,datetime, timedelta
from rest_framework.authtoken.models import Token
from django.db.models import Q, query
from licenseHolder.serializers import Planserializers
from licenseHolder.models import Plan
import pandas as pd
"""CLIENT REGISTRATION BY SUPERUSER"""
class AdminCheckClient(APIView):
    #permission_classes = [IsAdminUser]
    
    def get(self,request):
        client_get_query=request.GET.get('client_id')
        response={}
        if client_get_query is not None:

            get_client=Client.objects.get(client_id=client_get_query,status=True)
            serializers=ClientSerializers(get_client).data
            serializers.update({"username":get_client.user.username,"email":get_client.user.email})
            #liecense=License.objects.filter(client_id= get_client)
            # if len(liecense)>1:
            #     serializers=ClientLicenseSerializers(liecense,many=True).data
            # else:
            #     serializers=ClientLicenseSerializers(liecense[0],many=False).data
       
            return Response(serializers,status=status.HTTP_200_OK)
        else:
       
            get_all_client=Client.objects.filter(user__is_superuser=False,status=True).order_by('-create_date')
            for  client in get_all_client:
                username=User.objects.get(username=client.user.username)
                clientserializer=ClientSerializers(client,many=False).data
                clientserializer.update({"username":username.username,"email":username.email})
                response[client.id]=clientserializer
            return Response(response.values(),status=status.HTTP_200_OK)
    
    def post(self,request):
        data=request.data 
        client_info=Client.objects.filter(Q(company_name=data['company_name'])| Q(gstin=data['gstin']))
        if client_info.exists():
            return Response({"message":" company  Name or gst no already exists",'status':True},status=status.HTTP_400_BAD_REQUEST)
        
       
        
        client_username_create=User.objects.create(username=data['email'],email=data['email'],password=data['password'])
        try:
            Token.objects.create(user=client_username_create)
        except Exception as msg:
            return Response({"message":str(msg),"status":False},status=status.HTTP_400_BAD_REQUEST)
        try:
            client=Client.objects.create(user=client_username_create,company_name=data['company_name'],
                                countryCode=data['countryCode'],gstin=data['gstin'],state=data['state']
                                ,city=data['city'],addres=data['addres'],pincode=int(data['pincode']) ,
                                client_id=generate_client_id(),client_name=data['client_name'],phone_number=data['phone_number']

                                )
            return Response({"client_id":client.client_id,
                            'client_status':client.client_status,
                            },status=status.HTTP_200_OK)
        except Exception as msg:
            client_username_create.delete()
            return Response({"message":str(msg)})



    def put(self,request):
        client_update_query=request.GET.get('client_id')
        get_client=Client.objects.get(client_id=client_update_query)
        serializers=ClientSerializers(get_client,data=request.data,partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response({"message":"client updated successful","status":True},status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        client_get_query=request.GET.get('client_id')
        parmanent_delete=request.GET.get('status')#True False
        
        try:
            client=Client.objects.get(client_id=client_get_query)
        except Exception as msg:
            return Response({"message":"client id is not found","status":False},status=status.HTTP_400_BAD_REQUEST)
        
        if client_get_query is not None and parmanent_delete is not None:
            client.status=False
            client.save()
            return Response({"message":"client is deleted successful","status":True},status=status.HTTP_200_OK)
        else:
            client.delete()
            return Response({"message":"client is deleted successful","status":True},status=status.HTTP_200_OK)


"""SUPER ADMIN CHECK ALL LICENSE"""
class Client_license(APIView):
    def get(self,request):
        clientid=request.GET.get('client_id')
        response={}
        if clientid:
            try:
                client=Client.objects.get(client_id=clientid,client_status=True)
            except Exception as msg:
                return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)
            liecense=License.objects.filter(client_id=client,license_status=True)
            response={
                    "client_id":client.client_id,
                    "company_name":client.company_name,
                    "created_at":liecense.order_by('created_at'). values_list('created_at').distinct(),
                    "end_at":liecense.order_by('end_at').values_list('end_at').distinct(),
                    "active_license":liecense.filter(active_license=True).count(),
                    "license_status":liecense.count()#number of license client have
                }
            return Response(response,status=status.HTTP_200_OK)
            
        else:
            clients=Client.objects.filter(client_status=True)
            for client in clients:
                liecense=License.objects.filter(client_id=client,license_status=True)
                response[client.id]={
                    "client_id":client.client_id,
                    "company_name":client.company_name,
                    "created_at":liecense.order_by('created_at'). values_list('created_at').distinct(),
                    "end_at":liecense.order_by('end_at').values_list('end_at').distinct(),
                    "active_license":liecense.filter(active_license=True).count(),
                    "license_status":liecense.count()#number of license client have
                }
            return Response(response.values(),status=status.HTTP_200_OK)
            

    def post(self,request):
        clientid=request.GET.get('client_id')
        

        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True
        
        
        if clientid :


            try:
                client=Client.objects.get(client_id=clientid)
            except Exception as msg:
                return Response({"message":"client id not found"},status=status.HTTP_400_BAD_REQUEST)

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

    def delete(self,request):
        licenseid=request.GET.get('license_id')
        if licenseid is not None:
            try:
                license=License.objects.get(id=licenseid)
            except Exception as msg:
                return Response({"message":str(msg)})
            license.license_status=False
            license.save()
            return Response({"message":licenseid+"this license id deactivated","status":True},status=status.HTTP_200_OK)
        else:
            return Response({"message":"key errors"},status=status.HTTP_200_OK)



"""PLAN GET POST PUT DELETE"""
class Plan_Post(APIView):
    def get(self,request):
        planid=request.GET.get('plan_id')
        if planid:
            serializers=Planserializers(Plan.objects.get(id=planid),many=False).data
            return Response(serializers,status=status.HTTP_200_OK)  
        else:

            serializers=Planserializers(Plan.objects.all(),many=True).data
            return Response(serializers,status=status.HTTP_200_OK)   
    
    def post(self,request):
        data=request.data 
        serializers=Planserializers(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response({"message":"plan posted"})
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)




########QUALITY RELATED API  AND EXCEL UPLOAD START HERE###############

"""QUALITY CHECK LIST  """
class Quality_Check_List(APIView):
   
    def get(self,request):
        res={}
        qualitycheaklist=request.GET.get('quality_id')
        qualityquestion=request.GET.get('question_qualityid')
        if qualitycheaklist is not None:
            qualityid=get_object_or_404(QualityCheckList,id=qualitycheaklist) 
            serializers=QualitySerializer(qualityid,many=False)
            return Response(serializers.data,status=status.HTTP_200_OK)
        elif qualityquestion:
            questions=QualityQuestion.objects.filter(quality__id=qualityquestion)
            for qu in questions:
                serializer=QualityQuestionSerializers(qu,many=False).data
                serializer.update({"qualityid":qu.quality.qualityid})
                res[qu.id]=serializer
            return Response(res.values(),status=status.HTTP_200_OK)
        else:
            serializers=QualitySerializer(QualityCheckList.objects.all(),many=True)
            return Response(serializers.data,status=status.HTTP_200_OK)


    def post(self,request):
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        data['qualityid']=qualitycheacklist()
        serializers=QualitySerializer(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response({"message":"Quality check list posted","status":True},status=status.HTTP_200_OK)
        else:
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def put(self,request):
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        qualitycheaklist=request.GET.get('quality_id')
        if qualitycheaklist is not None:
            qualityid=get_object_or_404(QualityCheckList,id=qualitycheaklist) 
            serializers=QualitySerializer(qualityid,data=data,partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response({"message":"Quality check list updated","status":True},status=status.HTTP_200_OK)
            else:
                return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"key is requeired","status":True},status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request):
        qualitycheaklist=request.GET.get('quality_id')
        if qualitycheaklist is not None:
            qualityid=get_object_or_404(QualityCheckList,id=qualitycheaklist).delete()
            # if qualityid.status==True:

            #     qualityid.status=False 
            #     qualityid.save()
            return Response({"message":"quality check list deactivate","status":True},status=status.HTTP_200_OK)
            
        else:
            return Response({"message":"key requeired","status":False},status=status.HTTP_404_NOT_FOUND)
        
"""EXCEL UPLOAD CHECKLIST"""
class ExcelUploadQuality(APIView):
    def post(self,request):
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        data['file']=request.FILES['file']
        df=pd.read_excel(data['file'],header= 1, index_col= False)
        rows,col=df.shape
        for index in range(rows):
            if QualityCheckList.objects.filter(name=df["Name"][index]).exists()==False:
                QualityCheckList.objects.get_or_create(
                    name=df["Name"][index],
                    activate=df["Available"][index],
                    qualityid=qualitycheacklist(),
                    status=True
                    
                    ) 
            else:
                pass  
        return Response({"message":"quality checklist successful upload","status":True},status=status.HTTP_200_OK)


"""QUALITY CHECK LIST QUESTION """
class QualityCheackListQustion(APIView):
    def get(self,request):
        questionid=request.GET.get('question_id')
       
        if questionid:
            serializer=QualityQuestionSerializers(get_object_or_404(QualityQuestion,id=questionid),many=False)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            serializer=QualityQuestionSerializers(QualityQuestion.objects.all(),many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        print(data['quality'])
        qualitychecklistid=get_object_or_404(QualityCheckList,id=data['quality'] )
        data['quality'] = qualitychecklistid.id
        data['questionid']=qualityquestionid()
        serializer=QualityQuestionSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"quality question posted successful"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def put(self,request):
        questionid=request.GET.get('question_id')
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        try:
            qualityquestion=QualityQuestion.objects.get(id=questionid )
        except Exception as msg:
            return Response({"message":str(msg)})
        try:
            qualitychecklistid=QualityCheckList.objects.get(id=data['quality'] )
        except Exception as msg:
            return Response({"message":str(msg)})

        data['quality'] = qualitychecklistid.id
        
        serializer=QualityQuestionSerializers(qualityquestion,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"quality question posted successful"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self,request):
        qualityquestion=request.GET.get('question_id')
        get_object_or_404(QualityQuestion,id=qualityquestion).delete()
        return Response({"message":"Qualitycheck list  question deleted","status":True},status=status.HTTP_200_OK)


"""QUALITY QUESTION UPLOAD FORMAT EXCEL"""

class QualityQuestionUploadExcel(APIView):
    def post(self,request):
        data=request.data
       
        if not request.POST._mutable:
            request.POST._mutable = True 
        data['file']=request.FILES['file']
        df=pd.read_excel(data['file'],header= 1, index_col= False)
        rows,col=df.shape
        for index in range(rows):
            try:
                qualitychecklist=QualityCheckList.objects.get(qualityid=df["Code"][index])
            except Exception as msg:
                return Response({"message":str(msg),"status":False},status=status.HTTP_404_NOT_FOUND)
            
            if  QualityQuestion.objects.filter (quality=qualitychecklist,name=df["Checklist Questions"][index]).exists()==False:

                QualityQuestion.objects.get_or_create(
                                quality=qualitychecklist,
                                name=df["Checklist Questions"][index],
                                status=df['Status'][index],
                                questionid=qualityquestionid(),
                                activate=True
                                )  
            else:
                pass
        return Response({"message":"Quality question created","status":False},status=status.HTTP_201_CREATED)





######SAFTY CHECKLIST API AND EXCEL UPLOAD START FROM HERE#######
"""SEFTY CHECK LIST"""
class Sefty_Check_List(APIView):
    
    def get(self,request):
        res={}
        seftycheaklist=request.GET.get('safty_id')
        seftyquestion=request.GET.get('question_seftyid')
        if seftycheaklist is not None:
            seftyid=get_object_or_404(SeftyCheckList,id=seftycheaklist) 
            serializers=SeftySerializer(seftyid,many=False)
            return Response(serializers.data,status=status.HTTP_200_OK)
        
        elif seftyquestion:
            questions=SeftyQuestion.objects.filter(sefty__id=seftyquestion)
            for qu in questions:
                serializer=SeftyQuestionSerializers(qu,many=False).data
                serializer.update({"saftychecklistid":qu.sefty.saftychecklistid})
                res[qu.id]=serializer
            return Response(res.values(),status=status.HTTP_200_OK)
        else:
            serializers=SeftySerializer(SeftyCheckList.objects.all(),many=True)
            return Response(serializers.data,status=status.HTTP_200_OK)


    def post(self,request):
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        data['saftychecklistid']=seftycheacklist()
        serializers=SeftySerializer(data=data)
        if serializers.is_valid():
            serializers.save()
            return Response({"message":"Selty check list posted","status":True},status=status.HTTP_200_OK)
        else:
            return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def put(self,request):
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        seftycheaklist=request.GET.get('safty_id')
        if seftycheaklist is not None:
            seftyid=get_object_or_404(SeftyCheckList,id=seftycheaklist)
            serializers=SeftySerializer(seftyid,data=data,partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response({"message":"Selty check list posted","status":True},status=status.HTTP_200_OK)
            else:
                return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"key is requeired","status":True},status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request):
        seftycheaklist=request.GET.get('safty_id')
        if seftycheaklist is not None:
            get_object_or_404(SeftyCheckList,id=seftycheaklist).delete()
            return Response({"message":"Selty check list deactivate","status":True},status=status.HTTP_200_OK)
        else:
            return Response({"message":"key requeired"},status=status.HTTP_404_NOT_FOUND)


"""EXCEL UPLOAD  SAFTY CHECKLIST"""
class ExcelUploadSafty(APIView):
    def post(self,request):
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        data['file']=request.FILES['file']
        df=pd.read_excel(data['file'],header= 1, index_col= False)
        rows,col=df.shape
        for index in range(rows):
            if SeftyCheckList.objects.filter(name=df["Name"][index]).exists()==False:
                
                SeftyCheckList.objects.get_or_create(
                    name=df["Name"][index],
                    activate=df["Available"][index],
                    saftychecklistid=seftycheacklist(),
                    status=True
                    
                    ) 
            else:
                pass
            
        return Response({"message":"quality checklist successful upload","status":True},status=status.HTTP_200_OK)



"""SEFTY CHECK LIST QUESTION"""
class SeftyCheackListQustion(APIView):
    
    def get(self,request):
        seftyquestionid=request.GET.get('question_id')
        if seftyquestionid:
            serializer=SeftyQuestionSerializers(get_object_or_404( SeftyQuestion,id=seftyquestionid),many=False)
        else:
            serializer=SeftyQuestionSerializers(SeftyQuestion.objects.all(),many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True

        seftychecklistid=get_object_or_404(SeftyCheckList,id=data['sefty'] )
        data['sefty'] = seftychecklistid.id
        data['questionid']=seftyquestionid()
        serializer=SeftyQuestionSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"sefty question posted successful"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request):
        questionid=request.GET.get('question_id')
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        try:
            seftyquestion=SeftyQuestion.objects.get(id=questionid )
        except Exception as msg:
            return Response({"message":str(msg)})
        try:
            qualitychecklistid=SeftyCheckList.objects.get(id=seftyquestion.sefty.id )
        except Exception as msg:
            return Response({"message":str(msg)})

        data['sefty'] = qualitychecklistid.id 
        serializer=QualityQuestionSerializers(seftyquestion,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"quality question posted successful"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request):
        saftyquestion=request.GET.get('question_id')
        get_object_or_404(SeftyQuestion,id=saftyquestion).delete()
        return Response({"message":"safty question deleted","status":True},status=status.HTTP_200_OK)


"""SAFTY QUESTION UPLOAD QUESTION UPLOAD THROUGH EXCEL"""
class SaftyQuestionUploadExcel(APIView):
    def post(self,request):
        data=request.data
        if not request.POST._mutable:
            request.POST._mutable = True 
        data['file']=request.FILES['file']
        df=pd.read_excel(data['file'],header= 1, index_col= False)
        rows,col=df.shape
        for index in range(rows):
            try:
                saftychecklist=SeftyCheckList.objects.get(saftychecklistid=df["Code"][index])
            except Exception as msg:
                return Response({"message":str(msg),"status":False},status=status.HTTP_404_NOT_FOUND)
            
            if  SeftyQuestion.objects.filter (sefty=saftychecklist,name=df["Checklist Questions"][index]).exists()==False:

                SeftyQuestion.objects.get_or_create(
                                sefty=saftychecklist,
                                name=df["Checklist Questions"][index],
                                status=df['Status'][index],
                                questionid=seftyquestionid(),
                                activate=True

                                )
            else:
                pass  
        return Response({"message":"safty question created","status":False},status=status.HTTP_201_CREATED)