from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationDetailSerializer,
    MessageSerializer
)
from properties.models import Property

class IsParticipant(permissions.BasePermission):
    """
    Custom permission: Only conversation participants can access
    """
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()

class ConversationListView(generics.ListAPIView):
    """
    GET /api/messaging/conversations/
    List all conversations for authenticated user
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages').order_by('-last_message_at')

class ConversationDetailView(generics.RetrieveAPIView):
    """
    GET /api/messaging/conversations/<id>/
    Get conversation details with all messages
    """
    serializer_class = ConversationDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    queryset = Conversation.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Mark all messages as read for the current user
        Message.objects.filter(
            conversation=instance,
            receiver=request.user,
            is_read=False
        ).update(is_read=True)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class StartConversationView(APIView):
    """
    POST /api/messaging/start/
    Start a new conversation about a property
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        property_id = request.data.get('property_id')
        initial_message = request.data.get('message')
        
        if not property_id or not initial_message:
            return Response({
                'error': 'property_id and message are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        property_obj = get_object_or_404(Property, id=property_id)
        
        # Check if conversation already exists
        existing_conversation = Conversation.objects.filter(
            property=property_obj,
            participants=request.user
        ).filter(
            participants=property_obj.owner
        ).first()
        
        if existing_conversation:
            # Use existing conversation
            conversation = existing_conversation
        else:
            # Create new conversation
            conversation = Conversation.objects.create(property=property_obj)
            conversation.participants.add(request.user, property_obj.owner)
        
        # Create initial message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            receiver=property_obj.owner,
            message_content=initial_message
        )
        
        return Response({
            'conversation_id': conversation.id,
            'message': MessageSerializer(message).data
        }, status=status.HTTP_201_CREATED)

class SendMessageView(generics.CreateAPIView):
    """
    POST /api/messaging/send/
    Send a message in a conversation
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation')
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if user is a participant
        if request.user not in conversation.participants.all():
            return Response({
                'error': 'You are not a participant in this conversation'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get the other participant as receiver
        receiver = conversation.get_other_participant(request.user)
        
        if not receiver:
            return Response({
                'error': 'Could not find receiver'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            receiver=receiver,
            message_content=request.data.get('message_content')
        )
        
        return Response(
            MessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )

class UnreadMessagesCountView(APIView):
    """
    GET /api/messaging/unread-count/
    Get count of unread messages
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        unread_count = Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
        
        return Response({
            'unread_count': unread_count
        })

class MarkMessageAsReadView(APIView):
    """
    POST /api/messaging/message/<id>/mark-read/
    Mark a message as read
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        message = get_object_or_404(Message, id=pk, receiver=request.user)
        
        if not message.is_read:
            from django.utils import timezone
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
        
        return Response({
            'message': 'Message marked as read'
        })

class DeleteConversationView(generics.DestroyAPIView):
    """
    DELETE /api/messaging/conversations/<id>/
    Delete a conversation
    """
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    queryset = Conversation.objects.all()