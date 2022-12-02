import base64
from django.core.files.base import ContentFile
def upload_image(uploadfile)
    format, imgstr = uploadfile.split(';base64,') 
    ext = format.split('/')[-1] 
    uploadfile = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    print("=====base64 change image====")
    # print(uploadfile)
    return uploadfile