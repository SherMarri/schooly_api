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
            'fullname': user.profile.fullname
        }
        return data


class StudentProfileSerializer(serializers.ModelSerializer):

    roll_number = serializers.SerializerMethodField()

    class Meta:
        model = models.Profile
        fields = ('id', 'fullname', 'roll_number', 'user_id')

    def get_roll_number(self, obj):
        try:
            return obj.student_info.roll_number
        except:
            return None
