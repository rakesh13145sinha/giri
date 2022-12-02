from django import urls
from .views import *
from django.urls import path,include

urlpatterns=[
    
    path('client/', include([
            path('login',Loggin.as_view()),
            path('registration',Client_Registration.as_view()),
            path('logout',Logout.as_view()),
            path('otp',SendOpt.as_view()),
           
           
    
    ])),
        
    
    
]