from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import PropertyApplication
from .serializers import (
    PropertyApplicationSerializer,
    ApplicationResponseSerializer,
    ApplicationDetailSerializer
)
from properties.models import Property
from notifications.models import Notification

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Tenant can view their own applications,
    Landlord can view applications for their properties
    """
    def has_object_permission(self, request, view, obj):
        # Tenant can view their own application
        if obj.tenant == request.user:
            return True
        # Landlord can view applications for their property
        if obj.property.owner == request.user:
            return True
        return False

class SubmitApplicationView(generics.CreateAPIView):
    """
    POST /api/applications/submit/
    Submit a rental application
    """
    serializer_class = PropertyApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Check if user is trying to apply to their own property
        property_id = request.data.get('property')
        property_obj = get_object_or_404(Property, id=property_id)
        
        if property_obj.owner == request.user:
            return Response({
                'error': 'You cannot apply to your own property'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is verified (optional requirement)
        if request.user.user_type == 'LANDLORD':
            return Response({
                'error': 'Landlords cannot apply for properties. Please switch to tenant mode.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)

class MyApplicationsView(generics.ListAPIView):
    """
    GET /api/applications/my-applications/
    List all applications submitted by the authenticated user
    """
    serializer_class = PropertyApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PropertyApplication.objects.filter(
            tenant=self.request.user
        ).select_related('property', 'property__owner').order_by('-applied_at')

class PropertyApplicationsView(generics.ListAPIView):
    """
    GET /api/applications/property/<property_id>/
    List all applications for a specific property (Landlord only)
    """
    serializer_class = PropertyApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        property_obj = get_object_or_404(Property, id=property_id, owner=self.request.user)
        
        return PropertyApplication.objects.filter(
            property=property_obj
        ).select_related('tenant', 'property').order_by('-applied_at')

class ApplicationDetailView(generics.RetrieveAPIView):
    """
    GET /api/applications/<id>/
    Get application details
    """
    serializer_class = ApplicationDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = PropertyApplication.objects.all()


class RespondToApplicationView(generics.UpdateAPIView):
    """
    PUT /api/applications/<id>/respond/
    Accept or reject an application (Landlord only)
    """
    serializer_class = ApplicationResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = PropertyApplication.objects.all()
    
    def get_queryset(self):
        # Only property owner can respond
        return PropertyApplication.objects.filter(
            property__owner=self.request.user
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.status != 'PENDING':
            return Response({
                'error': 'This application has already been processed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the application
        response = super().update(request, *args, **kwargs)
        
        # Refresh instance to get updated status
        instance.refresh_from_db()
        
        # Create notification for tenant
        Notification.objects.create(
            user=instance.tenant,
            notification_type='APPLICATION_ACCEPTED' if instance.status == 'ACCEPTED' else 'APPLICATION_REJECTED',
            title=f'Application {instance.status.title()}',
            message=f'Your application for "{instance.property.title}" has been {instance.status.lower()} by the landlord.',
            metadata={
                'application_id': str(instance.id),
                'property_id': str(instance.property.id)
            }
        )
        
        return response

class WithdrawApplicationView(APIView):
    """
    POST /api/applications/<id>/withdraw/
    Withdraw an application (Tenant only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        application = get_object_or_404(
            PropertyApplication,
            id=pk,
            tenant=request.user
        )
        
        if application.status != 'PENDING':
            return Response({
                'error': 'Only pending applications can be withdrawn'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'WITHDRAWN'
        application.save()
        
        return Response({
            'message': 'Application withdrawn successfully'
        }, status=status.HTTP_200_OK)

class ReceivedApplicationsView(generics.ListAPIView):
    """
    GET /api/applications/received/
    List all applications received for landlord's properties
    """
    serializer_class = PropertyApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PropertyApplication.objects.filter(
            property__owner=self.request.user
        ).select_related('tenant', 'property').order_by('-applied_at')
    
