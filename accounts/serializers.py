from rest_framework import serializers

from accounts import models


class JWTUserDetailsSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user = obj['user']
        data = {
            'username': user.username,
            'role': user.profile.get_profile_type_display(),
            'fullname': user.profile.info.fullname
        }
        return data


class StudentInfoSerializer(serializers.ModelSerializer):

    user_id = serializers.SerializerMethodField()

    class Meta:
        model = models.StudentInfo
        fields = ('id', 'fullname', 'roll_number', 'user_id')

    def get_user_id(self, obj):
        return obj.profile.first().user_id
