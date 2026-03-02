from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'user', 'notification_type', 'title', 'message', 
                  'metadata', 'is_read', 'read_at', 'created_at')
        read_only_fields = ('id', 'user', 'read_at', 'created_at')

class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('user', 'notification_type', 'title', 'message', 'metadata')
