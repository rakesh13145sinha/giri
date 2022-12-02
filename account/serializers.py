from rest_framework import serializers
from .models import *

class ClientSerializers(serializers.ModelSerializer):
    class Meta:
        model=Client 
        fields='__all__'

class ClientLicenseSerializers(serializers.ModelSerializer):
    class Meta:
        model=License 
        exclude=['client_id']