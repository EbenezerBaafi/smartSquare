from rest_framework import serializers
from .models import PropertyApplication
from properties.serializers import PropertyListSerializer
from accounts.serializers import UserSerializer

class PropertyApplicationSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.full_name', read_only=True)
    tenant_email = serializers.EmailField(source='tenant.email', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_owner = serializers.CharField(source='property.owner.full_name', read_only=True)
    
    class Meta:
        model = PropertyApplication
        fields = ('id', 'property', 'property_title', 'property_owner', 'tenant', 
                  'tenant_name', 'tenant_email', 'status', 'message', 
                  'landlord_response', 'move_in_date', 'lease_duration_months', 
                  'applied_at', 'responded_at', 'created_at', 'updated_at')
        read_only_fields = ('id', 'tenant', 'status', 'landlord_response', 
                           'applied_at', 'responded_at', 'created_at', 'updated_at')
    
    def validate_property(self, value):
        # Check if property is available
        if value.listing_status != 'ACTIVE':
            raise serializers.ValidationError("This property is not available for applications.")
        
        # Check if user already has a pending application for this property
        user = self.context['request'].user
        if PropertyApplication.objects.filter(
            property=value, 
            tenant=user, 
            status='PENDING'
        ).exists():
            raise serializers.ValidationError("You already have a pending application for this property.")
        
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['tenant'] = user
        return super().create(validated_data)

class ApplicationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyApplication
        fields = ('status', 'landlord_response')
    
    def validate(self, attrs):
        if attrs.get('status') == 'REJECTED' and not attrs.get('landlord_response'):
            raise serializers.ValidationError({
                "landlord_response": "Please provide a reason for rejection."
            })
        return attrs
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        
        instance.status = validated_data.get('status', instance.status)
        instance.landlord_response = validated_data.get('landlord_response', instance.landlord_response)
        instance.responded_at = timezone.now()
        instance.save()
        
        # If accepted, update property status and reject other applications
        if instance.status == 'ACCEPTED':
            instance.property.listing_status = 'RENTED'
            instance.property.save()
            
            # Reject all other pending applications for this property
            PropertyApplication.objects.filter(
                property=instance.property,
                status='PENDING'
            ).exclude(id=instance.id).update(
                status='REJECTED',
                landlord_response='Property has been rented to another applicant.',
                responded_at=timezone.now()
            )
        
        return instance

class ApplicationDetailSerializer(serializers.ModelSerializer):
    tenant = UserSerializer(read_only=True)
    property = PropertyListSerializer(read_only=True)
    
    class Meta:
        model = PropertyApplication
        fields = '__all__'