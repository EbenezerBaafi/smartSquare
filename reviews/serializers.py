from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.full_name', read_only=True)
    reviewer_profile_picture = serializers.ImageField(source='reviewer.profile_picture', read_only=True)
    reviewee_name = serializers.CharField(source='reviewee.full_name', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'reviewer', 'reviewer_name', 'reviewer_profile_picture',
                  'reviewee', 'reviewee_name', 'property', 'property_title',
                  'rating', 'review_text', 'review_type', 'is_verified_stay',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'reviewer', 'is_verified_stay', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        review_type = attrs.get('review_type')
        property_obj = attrs.get('property')
        reviewee = attrs.get('reviewee')
        
        # Validate that property reviews have a property
        if review_type == 'PROPERTY' and not property_obj:
            raise serializers.ValidationError({
                "property": "Property is required for property reviews."
            })
        
        # Validate that user reviews have a reviewee
        if review_type in ['TENANT_TO_LANDLORD', 'LANDLORD_TO_TENANT'] and not reviewee:
            raise serializers.ValidationError({
                "reviewee": "Reviewee is required for user reviews."
            })
        
        return attrs
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['reviewer'] = user
        
        # Check if user has stayed at this property (simplified logic)
        # In production, you'd check if they had an accepted application
        if validated_data.get('property'):
            from applications.models import PropertyApplication
            has_stayed = PropertyApplication.objects.filter(
                tenant=user,
                property=validated_data['property'],
                status='ACCEPTED'
            ).exists()
            validated_data['is_verified_stay'] = has_stayed
        
        return super().create(validated_data)