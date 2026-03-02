from rest_framework import serializers
from .models import Conversation, Message
from accounts.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.full_name', read_only=True)
    
    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'sender_name', 'receiver', 
                  'receiver_name', 'message_content', 'is_read', 'read_at', 'sent_at')
        read_only_fields = ('id', 'sender', 'is_read', 'read_at', 'sent_at')
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['sender'] = user
        return super().create(validated_data)

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    property_title = serializers.CharField(source='property.title', read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'property', 'property_title', 'participants', 
                  'last_message', 'unread_count', 'last_message_at', 'created_at')
        read_only_fields = ('id', 'last_message_at', 'created_at')
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'sender': last_msg.sender.full_name,
                'content': last_msg.message_content[:50],
                'sent_at': last_msg.sent_at
            }
        return None
    
    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.messages.filter(receiver=user, is_read=False).count()

class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'property', 'property_title', 'participants', 
                  'messages', 'last_message_at', 'created_at')
        read_only_fields = ('id', 'last_message_at', 'created_at')