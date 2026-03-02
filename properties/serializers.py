from rest_framework import serializers
from .models import (
    Property, PropertyImage, PropertyAmenity, 
    PropertyDocument, SavedProperty, PropertyView
)

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ('id', 'image_url', 'thumbnail_url', 'display_order', 
                  'is_primary', 'caption', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')

class PropertyAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyAmenity
        fields = ('id', 'amenity_name', 'amenity_category')
        read_only_fields = ('id',)

class PropertyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyDocument
        fields = ('id', 'document_type', 'document_url', 'document_name', 
                  'is_required_for_verification', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')

class PropertyListSerializer(serializers.ModelSerializer):
    """Brief serializer for property listings"""
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    amenities_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ('id', 'title', 'property_type', 'listing_status', 'price_per_month', 
                  'currency', 'city', 'state', 'bedrooms', 'bathrooms', 'is_furnished',
                  'pets_allowed', 'owner_name', 'primary_image', 'view_count', 
                  'is_verified', 'amenities_count', 'created_at')
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            if request and primary.image_url:
                return request.build_absolute_uri(primary.image_url.url)
        return None
    
    def get_amenities_count(self, obj):
        return obj.amenities.count()

class PropertyDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single property view"""
    owner_name = serializers.CharField(source='owner.full_name', read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_phone = serializers.CharField(source='owner.phone_number', read_only=True)
    owner_profile_picture = serializers.ImageField(source='owner.profile_picture', read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    amenities = PropertyAmenitySerializer(many=True, read_only=True)
    documents = PropertyDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('id', 'owner', 'view_count', 'is_verified', 
                           'verified_by', 'verified_at', 'created_at', 'updated_at')

class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    amenities = PropertyAmenitySerializer(many=True, required=False)
    
    class Meta:
        model = Property
        exclude = ('owner', 'view_count', 'is_verified', 'verified_by', 'verified_at')
    
    def validate(self, attrs):
        # Only verified owners can set status to ACTIVE
        request = self.context.get('request')
        if request and not request.user.is_verified:
            if attrs.get('listing_status') == 'ACTIVE':
                raise serializers.ValidationError({
                    "listing_status": "You must be a verified property owner to activate listings."
                })
        return attrs
    
    def create(self, validated_data):
        amenities_data = validated_data.pop('amenities', [])
        user = self.context['request'].user
        property_obj = Property.objects.create(owner=user, **validated_data)
        
        # Create amenities
        for amenity_data in amenities_data:
            PropertyAmenity.objects.create(property=property_obj, **amenity_data)
        
        return property_obj
    
    def update(self, instance, validated_data):
        amenities_data = validated_data.pop('amenities', None)
        
        # Update property fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update amenities if provided
        if amenities_data is not None:
            instance.amenities.all().delete()
            for amenity_data in amenities_data:
                PropertyAmenity.objects.create(property=instance, **amenity_data)
        
        return instance

class SavedPropertySerializer(serializers.ModelSerializer):
    property_details = PropertyListSerializer(source='property', read_only=True)
    
    class Meta:
        model = SavedProperty
        fields = ('id', 'property', 'property_details', 'notes', 'saved_at')
        read_only_fields = ('id', 'saved_at')
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

class PropertyViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyView
        fields = ('id', 'property', 'user', 'ip_address', 'viewed_at')
        read_only_fields = ('id', 'user', 'viewed_at')