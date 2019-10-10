from rest_framework import serializers
from notifications import models


class NotificationSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Notification
        fields = ('id', 'title', 'creator', 'content', 'created_by', 'created_at',
                  'target_type', 'target_id')
        read_only_fields = ('creator',)

    def get_creator(self, instance):
        if not instance.created_by:
            return None
        return {
            'id': instance.created_by.id,
            'fullname': instance.created_by.profile.fullname,
        }

    def validate_created_by(self, user):
        try:
            if self.context['request'].user.id == user.id:
                return user
        except:
            raise serializers.ValidationError('Invalid user id')
        else:
            raise serializers.ValidationError('Invalid user id')
