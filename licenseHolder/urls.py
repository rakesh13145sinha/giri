from django.urls import path ,include
from .views import *
urlpatterns=[

    path('license/',include([
        
            path('create',Licence.as_view()),
            path('assign',Employee_Registration.as_view()),
            path('vendor',Vendor_Add.as_view()),
            path('material',Material_Add.as_view()),
            path('project/',include([
                                path('create',Project_Create.as_view()),
                                path('area/inspection/detail',Being_Inspected_Area_Details.as_view()),
                                path('area/inspection/submit',SubmissionOf_Inspected_Area_Details.as_view()),
                                path('area/inspection/submit/image',SubmissionOf_Inspected_Area_image.as_view())
                                
                                ])),

            path('send/',SendEmail.as_view()),
            path('send/otp',SendOpt.as_view()),
            path('send/otp/verification',OtpVerificaton.as_view()),
            path('quality/',include([
                path('checklist',Add_Quality_CheakList.as_view()),
                path('checklist/question',Client_Add_QualityChecklist_Question.as_view()),

            ])),
            path('sefty/',include([

                path('checklist',Add_Sefty_CheakList.as_view()),
                path('checklist/question',Client_Add_SeftyChecklist_Question.as_view()),

                ])),
            
            


        ])),
    
    path("inspect/",include([
        path('list/reinspect',ListOfFailedCheckList.as_view()),
        path('list/reschedule',RescheduleDateForInspection.as_view())
    ])),    
   
   path('approver/',include([
    path('pending/inspection',ListOfInspection.as_view()),
    path("pending/inspection/individual",IndividualInspection.as_view()),
    path("report",ReportUpload.as_view())
   ])),
   
    path('site/',include([
        path('observation/',SiteObservationReportGenerate.as_view()),
        path("observation/image/",SiteObservationImage.as_view()),
    
   ])),
    
    path('ncr/',include([
        path('report/',NcrGenerate.as_view()),
        path("report/image/",NCRImage.as_view()),
    
   ])),
   
    



]