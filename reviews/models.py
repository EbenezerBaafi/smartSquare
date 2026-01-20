from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Review(models.Model):
    REVIEW_TYPE_CHOICES = [
        ('TENANT_TO_LANDLORD', 'Tenant to Landlord'),
        ('LANDLORD_TO_TENANT', 'Landlord to Tenant'),
        ('PROPERTY', 'Property Review'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reviewer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews_given')
    reviewee = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews_received', null=True, blank=True)
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    review_text = models.TextField()
    review_type = models.CharField(max_length=25, choices=REVIEW_TYPE_CHOICES)
    is_verified_stay = models.BooleanField(
        default=False, 
        help_text="True if reviewer actually stayed at this property"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        # Prevent duplicate reviews: one user can only review a property/user once
        unique_together = [
            ['reviewer', 'property'],
            ['reviewer', 'reviewee'],
        ]
    
    def __str__(self):
        if self.review_type == 'PROPERTY':
            return f"{self.reviewer.full_name} reviewed {self.property.title} - {self.rating}★"
        return f"{self.reviewer.full_name} reviewed {self.reviewee.full_name} - {self.rating}★"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate that property reviews have a property
        if self.review_type == 'PROPERTY' and not self.property:
            raise ValidationError("Property reviews must have a property specified")
        
        # Validate that user reviews have a reviewee
        if self.review_type in ['TENANT_TO_LANDLORD', 'LANDLORD_TO_TENANT'] and not self.reviewee:
            raise ValidationError("User reviews must have a reviewee specified")
        
        # Prevent self-reviews
        if self.reviewee and self.reviewer == self.reviewee:
            raise ValidationError("You cannot review yourself")