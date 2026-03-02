from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Review
from .serializers import ReviewSerializer
from properties.models import Property
from accounts.models import User

class IsReviewerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Reviewer can edit/delete their own reviews
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.reviewer == request.user

class CreateReviewView(generics.CreateAPIView):
    """
    POST /api/reviews/create/
    Create a new review
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        # Prevent duplicate reviews
        review_type = request.data.get('review_type')
        
        if review_type == 'PROPERTY':
            property_id = request.data.get('property')
            if Review.objects.filter(
                reviewer=request.user,
                property_id=property_id,
                review_type='PROPERTY'
            ).exists():
                return Response({
                    'error': 'You have already reviewed this property'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        elif review_type in ['TENANT_TO_LANDLORD', 'LANDLORD_TO_TENANT']:
            reviewee_id = request.data.get('reviewee')
            if Review.objects.filter(
                reviewer=request.user,
                reviewee_id=reviewee_id
            ).exists():
                return Response({
                    'error': 'You have already reviewed this user'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)

class PropertyReviewsView(generics.ListAPIView):
    """
    GET /api/reviews/property/<property_id>/
    List all reviews for a property
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        return Review.objects.filter(
            property_id=property_id,
            review_type='PROPERTY'
        ).select_related('reviewer').order_by('-created_at')

class UserReviewsView(generics.ListAPIView):
    """
    GET /api/reviews/user/<user_id>/
    List all reviews for a user (as reviewee)
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Review.objects.filter(
            reviewee_id=user_id
        ).select_related('reviewer').order_by('-created_at')

class MyReviewsView(generics.ListAPIView):
    """
    GET /api/reviews/my-reviews/
    List all reviews written by authenticated user
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(
            reviewer=self.request.user
        ).select_related('reviewee', 'property').order_by('-created_at')

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/reviews/<id>/
    PUT /api/reviews/<id>/
    DELETE /api/reviews/<id>/
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrReadOnly]
    queryset = Review.objects.all()

class PropertyAverageRatingView(APIView):
    """
    GET /api/reviews/property/<property_id>/average/
    Get average rating for a property
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, property_id):
        property_obj = get_object_or_404(Property, id=property_id)
        
        avg_rating = Review.objects.filter(
            property=property_obj,
            review_type='PROPERTY'
        ).aggregate(Avg('rating'))['rating__avg']
        
        review_count = Review.objects.filter(
            property=property_obj,
            review_type='PROPERTY'
        ).count()
        
        return Response({
            'property_id': str(property_id),
            'average_rating': round(avg_rating, 2) if avg_rating else 0,
            'review_count': review_count
        })

class UserAverageRatingView(APIView):
    """
    GET /api/reviews/user/<user_id>/average/
    Get average rating for a user
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        
        avg_rating = Review.objects.filter(
            reviewee=user
        ).aggregate(Avg('rating'))['rating__avg']
        
        review_count = Review.objects.filter(reviewee=user).count()
        
        return Response({
            'user_id': str(user_id),
            'user_name': user.full_name,
            'average_rating': round(avg_rating, 2) if avg_rating else 0,
            'review_count': review_count
        })