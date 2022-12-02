from django.shortcuts import render
from django.contrib.auth.models import User 
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate,logout,login
from rest_framework.authtoken.models import Token
from .models import *
from rest_framework import status
from .serializers import *
from django.db.models import Q, query
from .client import generate_client_id
import random
from account.send_otp import sending_otp
# Create your views here.

"""CLIENT REGISTRATION"""
class Client_Registration(APIView):
    def get(self,request):
        client_get_query=request.GET.get('client_id')
        get_client=Client.objects.get(client_id=client_get_query)
        serializers=ClientSerializers(get_client).data
        serializers.update({"email":get_client.user.email})
        
        """BINDING LICENSE IN CLIENT DETAILS"""
        liecense=License.objects.filter(client_id=get_client)
        if len(liecense)>1:
            licenseserializers=ClientLicenseSerializers(liecense,many=True).data
        else:
            if liecense.exists():
                licenseserializers=ClientLicenseSerializers(liecense[0],many=False).data
            else:
                licenseserializers=ClientLicenseSerializers(liecense,many=False).data


        serializers.update({"liecese":licenseserializers})
        return Response(serializers,status=status.HTTP_200_OK)
        
    """ANYBODY CAN ACCESS THIS METHOD"""    
    def post(self,request):
        data=request.data 
        username_existance=Client.objects.filter(Q(company_name=data['company_name']))
        if username_existance.exists():
            return Response({"message":"Company  Name already exists",'status':True},status=status.HTTP_400_BAD_REQUEST)
        
       
        
        client_username_create=User(username=data['email'],email=data['email'])
        client_username_create.set_password(data['password'])
        client_username_create.save()
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
        
    

"""CLIENT LOGIN API"""
class Loggin(APIView):
    
    """LOGIN IN FOR CLIENT"""
    def post(self,request):
        data=request.data
        username_existance =User.objects.filter(username=data['email']).exists()
        if username_existance:
            user=authenticate(request,username=data['email'],password=data['password'])
            print(user)
            if user is not None :
                if  user.is_superuser:
                    # 
                    login(request,user)
                    return Response({
                        "message":"login succussful",
                       
                        "super_user_satus":user.is_superuser,
                    })
                
                try:
                    client=Client.objects.get(user=user,client_status=True)
                   
                except Exception as msg:
                    return Response(
                        {
                            "message":"You can't loggin right now,Approval is still pendding wait for update"

                        })
                client_token=Token.objects.get(user=user)
                clientserializer=ClientSerializers(client,many=False).data
                clientserializer.update({"client_token":client_token.key,"super_user_satus":user.is_superuser})
                return Response(clientserializer,status=status.HTTP_200_OK)
            else:
                return Response({"message":"Enter password is wrong",},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message":"Enter Email address is not valid"},status=status.HTTP_404_NOT_FOUND)



"""LOGOUT FOR ALL TYPE OF USER"""
class Logout(APIView):
    def get(self,request):
        logout(request)
        return Response({"message":"Thank you for user civil seva","status":True},status=status.HTTP_200_OK)
        


class SendOpt(APIView):

    def post(self,request,format=None):
        data = request.data
        generated_otp = random.randint(1000,9999)
        
        try:
            sending_otp(generated_otp,data['phone_number'])
        except Exception as msg:
            return Response({"message":str(msg)})
    
        return Response({'status':True,
                        "phone":data['phone_number'],
                        'message':"Otp sented Successful"},status=status.HTTP_202_ACCEPTED)
