from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import PropertyOwnerVerification, VerificationDocument
from .serializers import (
    PropertyOwnerVerificationSerializer,
    VerificationSubmissionSerializer,
    VerificationDocumentSerializer,
    VerificationReviewSerializer
)

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission: Owner can view their own, admin can view all
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user

class SubmitVerificationView(generics.CreateAPIView):
    """
    POST /api/verification/submit/
    Submit a new verification request
    """
    serializer_class = VerificationSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Check if user already has a pending verification
        if PropertyOwnerVerification.objects.filter(
            user=request.user,
            status='PENDING'
        ).exists():
            return Response({
                'error': 'You already have a pending verification request'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)

class UploadVerificationDocumentView(APIView):
    """
    POST /api/verification/<verification_id>/upload-document/
    Upload a document for verification
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, verification_id):
        verification = get_object_or_404(
            PropertyOwnerVerification,
            id=verification_id,
            user=request.user
        )
        
        if verification.status != 'PENDING':
            return Response({
                'error': 'Cannot upload documents to a processed verification'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = VerificationDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save document with verification
        document = serializer.save(
            verification=verification,
            file_size=request.FILES['document_url'].size,
            document_name=request.FILES['document_url'].name
        )
        
        return Response(
            VerificationDocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )

class MyVerificationsView(generics.ListAPIView):
    """
    GET /api/verification/my-verifications/
    List all verifications for the authenticated user
    """
    serializer_class = PropertyOwnerVerificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PropertyOwnerVerification.objects.filter(
            user=self.request.user
        ).order_by('-submitted_at')

class VerificationDetailView(generics.RetrieveAPIView):
    """
    GET /api/verification/<id>/
    Get verification details
    """
    serializer_class = PropertyOwnerVerificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = PropertyOwnerVerification.objects.all()

class PendingVerificationsView(generics.ListAPIView):
    """
    GET /api/verification/pending/
    List all pending verifications (Admin only)
    """
    serializer_class = PropertyOwnerVerificationSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        return PropertyOwnerVerification.objects.filter(
            status='PENDING'
        ).order_by('-submitted_at')

class ReviewVerificationView(generics.UpdateAPIView):
    """
    PUT /api/verification/<id>/review/
    Approve or reject a verification (Admin only)
    """
    serializer_class = VerificationReviewSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = PropertyOwnerVerification.objects.all()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if instance.status != 'PENDING':
            return Response({
                'error': 'This verification has already been processed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().update(request, *args, **kwargs)

class DeleteVerificationDocumentView(generics.DestroyAPIView):
    """
    DELETE /api/verification/document/<id>/
    Delete a verification document
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = VerificationDocument.objects.all()
    
    def get_queryset(self):
        # Users can only delete their own documents
        return VerificationDocument.objects.filter(
            verification__user=self.request.user
        )