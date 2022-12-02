from django.contrib import admin
from .models import *

class QualityQuestionAdmin(admin.ModelAdmin):
    list_display=['questionid','quality']

class SeftyQuestionAdmin(admin.ModelAdmin):
    list_display=['questionid','sefty']


class SeftyCheckListAdmin(admin.ModelAdmin):
    list_display=['saftychecklistid','name','activate','status']
    list_editable=['status','activate']

class QualityCheckListAdmin(admin.ModelAdmin):
    list_display=['qualityid','name','activate','status']
    list_editable=['status','activate']


admin.site.register(QualityQuestion,QualityQuestionAdmin)
admin.site.register(SeftyCheckList,SeftyCheckListAdmin)
admin.site.register(QualityCheckList,QualityCheckListAdmin)
admin.site.register(SeftyQuestion,SeftyQuestionAdmin)
