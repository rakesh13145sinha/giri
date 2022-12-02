from django.db import models

from django.contrib.auth.models import User

from AdminUser.models import QualityCheckList, SeftyCheckList

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company_user")
    client_name=models.CharField(max_length=200,null=True)
    company_name = models.CharField(max_length=50,unique=True,null=True)
    countryCode = models.CharField(max_length=50)
    gstin = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone_number=models.CharField(max_length=50,unique=True,null=True,blank=True)
    addres = models.TextField(verbose_name ="Address",)
    pincode = models.PositiveIntegerField()
    client_id=models.CharField(max_length=100,null=True,blank=True)#on update it will fill
    license_purchased = models.PositiveIntegerField(blank=True, null=True,default=0)
    client_status=models.BooleanField(default=False)
    status=models.BooleanField(default=True)#for visibilty
    qualitychecklist=models.ManyToManyField(QualityCheckList,related_name="Qualitychecklist")
    seftychecklist=models.ManyToManyField(SeftyCheckList,related_name="Seftychecklist")
    create_date=models.DateTimeField(auto_now=True,auto_now_add=False)
    updated_date=models.DateTimeField(auto_now=False,auto_now_add=True)

    class Meta:
        ordering = ("-id",)
        
    def __str__(self):
        return self.company_name


class License(models.Model):
    SUBSCRIPTION=[
        ("M","MONTHY"),("A","ANNUAL")
    ]
    client_id = models.ForeignKey(Client,on_delete = models.CASCADE)
    license_id = models.CharField(max_length=20)
    price=models.CharField(max_length=50,null=True)
    subcription_plan=models.CharField(max_length=20, choices=SUBSCRIPTION,null=True,verbose_name="Subscription")
    created_at = models.DateField(verbose_name="Taken Date",null=True)
    end_at = models.DateField(verbose_name="End Date",null=True)
    license_status = models.BooleanField(default=True)
    active_license=models.BooleanField(default=False)
    create_date=models.DateTimeField(auto_now=False,auto_now_add=True,null=True)

    
    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return f"{self.license_id}"


# def save(self, *args, **kwargs):
#         self.slug = slugify(self.title)
#         super(GeeksModel, self).save(*args, **kwargs)