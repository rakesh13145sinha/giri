from django.db.models import fields
from rest_framework import serializers
from .models import *


class QualitySerializer(serializers.ModelSerializer):
    class Meta:
        model=QualityCheckList
        fields='__all__'

class SeftySerializer(serializers.ModelSerializer):
    class Meta:
        model=SeftyCheckList
        fields='__all__'

class QualityQuestionSerializers(serializers.ModelSerializer):
    class Meta:
        model=QualityQuestion
        fields='__all__'

class SeftyQuestionSerializers(serializers.ModelSerializer):
    class Meta:
        model=SeftyQuestion
        fields='__all__'