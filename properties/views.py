from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import (
    Property, PropertyImage, PropertyAmenity,
    SavedProperty, PropertyView
)
from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyCreateUpdateSerializer,
    PropertyImageSerializer,
    SavedPropertySerializer
)

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Owner can edit, others can only read
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class PropertyListCreateView(generics.ListCreateAPIView):
    """
    GET /api/properties/ - List all properties
    POST /api/properties/ - Create new property
    """
    queryset = Property.objects.filter(listing_status='ACTIVE')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'city', 'state', 'bedrooms', 'bathrooms', 'is_furnished', 'pets_allowed']
    search_fields = ['title', 'description', 'address_line1', 'city']
    ordering_fields = ['price_per_month', 'created_at', 'view_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PropertyCreateUpdateSerializer
        return PropertyListSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price_per_month__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_month__lte=max_price)
        
        return queryset.select_related('owner').prefetch_related('images', 'amenities')

class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/properties/<id>/ - Get property details
    PUT /api/properties/<id>/ - Update property
    DELETE /api/properties/<id>/ - Delete property
    """
    queryset = Property.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PropertyCreateUpdateSerializer
        return PropertyDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Track property view
        PropertyView.objects.create(
            property=instance,
            user=request.user if request.user.is_authenticated else None,
            ip_address=self.get_client_ip(request)
        )
        
        # Increment view count
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class MyPropertiesView(generics.ListAPIView):
    """
    GET /api/properties/my-properties/
    List all properties owned by authenticated user
    """
    serializer_class = PropertyListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Property.objects.filter(
            owner=self.request.user
        ).select_related('owner').prefetch_related('images', 'amenities')

class UploadPropertyImageView(APIView):
    """
    POST /api/properties/<property_id>/upload-image/
    Upload an image for a property
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, property_id):
        property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
        
        serializer = PropertyImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # If this is marked as primary, unset other primary images
        if serializer.validated_data.get('is_primary'):
            PropertyImage.objects.filter(property=property_obj, is_primary=True).update(is_primary=False)
        
        image = serializer.save(property=property_obj)
        
        return Response(
            PropertyImageSerializer(image).data,
            status=status.HTTP_201_CREATED
        )

class DeletePropertyImageView(generics.DestroyAPIView):
    """
    DELETE /api/properties/image/<id>/
    Delete a property image
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = PropertyImage.objects.all()
    
    def get_queryset(self):
        return PropertyImage.objects.filter(property__owner=self.request.user)

class SavePropertyView(APIView):
    """
    POST /api/properties/<property_id>/save/
    Save a property to favorites
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, property_id):
        property_obj = get_object_or_404(Property, id=property_id)
        
        saved_property, created = SavedProperty.objects.get_or_create(
            user=request.user,
            property=property_obj,
            defaults={'notes': request.data.get('notes', '')}
        )
        
        if not created:
            return Response({
                'message': 'Property already saved'
            }, status=status.HTTP_200_OK)
        
        return Response(
            SavedPropertySerializer(saved_property).data,
            status=status.HTTP_201_CREATED
        )

class UnsavePropertyView(APIView):
    """
    DELETE /api/properties/<property_id>/unsave/
    Remove property from favorites
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, property_id):
        saved_property = get_object_or_404(
            SavedProperty,
            user=request.user,
            property_id=property_id
        )
        saved_property.delete()
        
        return Response({
            'message': 'Property removed from saved list'
        }, status=status.HTTP_200_OK)

class SavedPropertiesView(generics.ListAPIView):
    """
    GET /api/properties/saved/
    List all saved properties
    """
    serializer_class = SavedPropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SavedProperty.objects.filter(
            user=self.request.user
        ).select_related('property__owner').prefetch_related('property__images')