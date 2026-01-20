from django.db import models
import uuid

class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('APARTMENT', 'Apartment'),
        ('HOUSE', 'House'),
        ('STUDIO', 'Studio'),
        ('ROOM', 'Room'),
        ('COMMERCIAL', 'Commercial'),
        ('HOSTEL', 'Hostel'),
    ]
    
    LISTING_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('RENTED', 'Rented'),
        ('INACTIVE', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    listing_status = models.CharField(max_length=10, choices=LISTING_STATUS_CHOICES, default='DRAFT')
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')
    
    # Address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    region = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Property details
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    square_feet = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_furnished = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    available_from = models.DateField()
    
    # Metadata
    view_count = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_properties')
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        return self.title

class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image_url = models.ImageField(upload_to='property_images/')
    thumbnail_url = models.ImageField(upload_to='property_thumbnails/', null=True, blank=True)
    display_order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.property.title} - Image {self.display_order}"

class PropertyAmenity(models.Model):
    AMENITY_CATEGORIES = [
        ('BASIC', 'Basic'),
        ('SAFETY', 'Safety'),
        ('KITCHEN', 'Kitchen'),
        ('OUTDOOR', 'Outdoor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='amenities')
    amenity_name = models.CharField(max_length=100)
    amenity_category = models.CharField(max_length=20, choices=AMENITY_CATEGORIES)
    
    class Meta:
        verbose_name_plural = 'Property Amenities'
    
    def __str__(self):
        return f"{self.property.title} - {self.amenity_name}"
    

class SavedProperty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='saved_properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='saved_by')
    notes = models.TextField(blank=True, help_text="Personal notes about this property")
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-saved_at']
        unique_together = ['user', 'property']  # Prevent duplicate saves
        verbose_name_plural = 'Saved Properties'
    
    def __str__(self):
        return f"{self.user.full_name} saved {self.property.title}"

class PropertyView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='property_views')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
    
    def __str__(self):
        viewer = self.user.full_name if self.user else f"Anonymous ({self.ip_address})"
        return f"{viewer} viewed {self.property.title}"


class PropertyDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('TITLE_DEED', 'Title Deed'),
        ('RENTAL_AGREEMENT', 'Rental Agreement'),
        ('INSPECTION_REPORT', 'Inspection Report'),
        ('OTHER', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_url = models.FileField(upload_to='property_documents/')
    document_name = models.CharField(max_length=255)
    is_required_for_verification = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.property.title} - {self.document_type}"