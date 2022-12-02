from django.db import models
from django.utils.translation import activate 

class QualityCheckList(models.Model):
    name=models.CharField(max_length=100,unique=True)
    qualityid=models.CharField(max_length=20)
    status=models.BooleanField(default=False)
    activate=models.BooleanField(default=False)
    about=models.CharField(default="quality",max_length=1000)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)
    updated_date=models.DateTimeField(auto_now_add=False,auto_now=True)

    def __str__(self):
        return self.name


class SeftyCheckList(models.Model):
    name=models.CharField(max_length=100,unique=True)
    saftychecklistid=models.CharField(max_length=20)
    status=models.BooleanField(default=False)
    activate=models.BooleanField(default=False)
    about=models.CharField(default="sefty",max_length=1000)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)
    updated_date=models.DateTimeField(auto_now_add=False,auto_now=True)

    def __str__(self):
        return self.name

class QualityQuestion(models.Model):
    quality=models.ForeignKey(QualityCheckList,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    questionid=models.CharField(max_length=255)
    status=models.BooleanField(default=False)
    activate=models.BooleanField(default=False)
    about=models.CharField(default="quality question",max_length=1000)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)
    updated_date=models.DateTimeField(auto_now_add=False,auto_now=True)

    def __str__(self):
        return self.name

class SeftyQuestion(models.Model):
    sefty=models.ForeignKey(SeftyCheckList,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    questionid=models.CharField(max_length=255)
    status=models.BooleanField(default=False)
    activate=models.BooleanField(default=False)
    about=models.CharField(default="safty qustion",max_length=1000)
    created_date=models.DateTimeField(auto_now=False,auto_now_add=True)
    updated_date=models.DateTimeField(auto_now_add=False,auto_now=True)

    def __str__(self):
        return self.name
