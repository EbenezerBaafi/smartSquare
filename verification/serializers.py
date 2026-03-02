from rest_framework import serializers
from .models import PropertyOwnerVerification, VerificationDocument

class VerificationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationDocument
        fields = ('id', 'document_type', 'document_url', 'document_name', 
                  'file_size', 'uploaded_at')
        read_only_fields = ('id', 'file_size', 'uploaded_at')
    
    def validate_document_url(self, value):
        # Validate file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only PDF and image files (JPEG, PNG) are allowed.")
        
        return value

class PropertyOwnerVerificationSerializer(serializers.ModelSerializer):
    documents = VerificationDocumentSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.full_name', read_only=True)
    
    class Meta:
        model = PropertyOwnerVerification
        fields = ('id', 'user', 'user_name', 'user_email', 'verification_type', 
                  'status', 'rejection_reason', 'verified_by', 'verified_by_name',
                  'submitted_at', 'verified_at', 'expires_at', 'documents', 
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'status', 'verified_by', 'verified_at', 
                           'submitted_at', 'created_at', 'updated_at')

class VerificationSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOwnerVerification
        fields = ('id', 'verification_type')
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

class VerificationReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOwnerVerification
        fields = ('status', 'rejection_reason')
    
    def validate(self, attrs):
        if attrs.get('status') == 'REJECTED' and not attrs.get('rejection_reason'):
            raise serializers.ValidationError({
                "rejection_reason": "Rejection reason is required when rejecting verification."
            })
        return attrs
    
    def update(self, instance, validated_data):
        from django.utils import timezone
        
        instance.status = validated_data.get('status', instance.status)
        instance.rejection_reason = validated_data.get('rejection_reason', instance.rejection_reason)
        instance.verified_by = self.context['request'].user
        instance.verified_at = timezone.now()
        
        if instance.status == 'APPROVED':
            # Set expiry to 1 year from now
            from datetime import timedelta
            instance.expires_at = timezone.now() + timedelta(days=365)
            
            # Mark user as verified
            instance.user.is_verified = True
            instance.user.save()
        
        instance.save()
        return instance