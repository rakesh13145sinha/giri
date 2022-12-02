from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SiteObservationReport,NonComplianceReport,ObservationReportImage,NonComplianceReportImage

# def generate_observation_id():
#     site=SiteObservationReport.objects.latest('id')
#     pattern="SOR"+"_"+site.client_id.client_id+"_"+site.project.projectId+"_"+str(site.id)
#     return pattern

def observation_image_id():
    site=ObservationReportImage.objects.latest('id')
    pattern="SOR"+"_"+"IMG"+"_"+str(site.id)
    return pattern
    


# def generate_ncr_id():
#     site=NonComplianceReport.objects.latest('id')
#     pattern="NCR"+"_"+site.client_id.client_id+"_"+site.project.projectId+"_"+str(site.id)
#     return pattern

def ncr_image_id():

    site=NonComplianceReportImage.objects.latest('id')
    pattern="NCR"+"_"+"IMG"+"_"+str(site.id)
    return pattern





# @receiver(post_save, sender=SiteObservationReport)
# def create_dating_profile(sender, instance, created, **kwargs):
#     if created:
#         instance.siteobsevationid=generate_observation_id()
#         instance.save()
        
        
@receiver(post_save, sender=ObservationReportImage)
def create_observation(sender, instance, created, **kwargs):
    if created:
        if instance.site_image_id is None:
            instance.site_image_id=observation_image_id()
            instance.save()
        else:
            pass

# @receiver(post_save, sender=NonComplianceReport)
# def create_ncr_report(sender, instance, created, **kwargs):
#     if created:
#         instance.ncrid=generate_ncr_id()
#         instance.save()
           
@receiver(post_save, sender=NonComplianceReportImage)
def create_ncr_image(sender, instance, created, **kwargs):
    if created:
        if instance.ncr_image_id is None:
            instance.ncr_image_id=ncr_image_id()
            instance.save()
        else:
            pass