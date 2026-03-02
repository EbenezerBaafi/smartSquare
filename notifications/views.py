from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    """
    GET /api/notifications/
    List all notifications for authenticated user
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

class UnreadNotificationsView(generics.ListAPIView):
    """
    GET /api/notifications/unread/
    List unread notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False
        ).order_by('-created_at')

class NotificationDetailView(generics.RetrieveAPIView):
    """
    GET /api/notifications/<id>/
    Get notification details
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class MarkNotificationReadView(APIView):
    """
    POST /api/notifications/<id>/mark-read/
    Mark a notification as read
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        notification = get_object_or_404(
            Notification,
            id=pk,
            user=request.user
        )
        notification.mark_as_read()
        
        return Response({
            'message': 'Notification marked as read'
        }, status=status.HTTP_200_OK)

class MarkAllNotificationsReadView(APIView):
    """
    POST /api/notifications/mark-all-read/
    Mark all notifications as read
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        from django.utils import timezone
        
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'{updated_count} notification(s) marked as read'
        }, status=status.HTTP_200_OK)

class DeleteNotificationView(generics.DestroyAPIView):
    """
    DELETE /api/notifications/<id>/
    Delete a notification
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.get_queryset(), id=pk)

class UnreadCountView(APIView):
    """
    GET /api/notifications/unread-count/
    Get count of unread notifications
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({
            'unread_count': unread_count
        })