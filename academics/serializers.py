from academics import models
from rest_framework import serializers


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subject
        fields = ('id', 'name')