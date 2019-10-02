from academics import models
from structure import models as structure_models
from rest_framework import serializers


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subject
        fields = ('id', 'name')


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = structure_models.Section
        fields = ('id', 'name', 'grade')


class GradeSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = structure_models.Grade
        fields = ('id', 'name', 'sections')
