from django.urls import path ,include 
from .views import *
urlpatterns=[ 
    
    
    path('client/',include([
        path('registration',AdminCheckClient.as_view()),
        path('licence',Client_license.as_view()),
        path('plan',Plan_Post.as_view()),
    ])),
    path('checklist/',include([
        path('quality',Quality_Check_List.as_view()),
        path('quality/excel',ExcelUploadQuality.as_view()),
        
        path('sefty',Sefty_Check_List.as_view()),
        path('safty/excel',ExcelUploadSafty.as_view()),
        path('quality/question',QualityCheackListQustion.as_view()),
        path('quality/question/excel',QualityQuestionUploadExcel.as_view()),
        path('sefty/question',SeftyCheackListQustion.as_view()),
        path('safty/question/excel',SaftyQuestionUploadExcel.as_view()),
       
    ])),
    

    
    

]