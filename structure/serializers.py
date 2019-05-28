from rest_framework import serializers
from structure import models


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Section
        fields = ('id', 'name', 'grade')


class GradeSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    
    class Meta:
        model = models.Grade
        fields = ('id', 'name', 'sections')
