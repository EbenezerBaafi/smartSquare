from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Property, PropertyImage, PropertyAmenity, 
    PropertyDocument, SavedProperty, PropertyView
)

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ('uploaded_at', 'image_preview')
    fields = ('image_url', 'image_preview', 'display_order', 'is_primary', 'caption')
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.image_url.url)
        return "No image"
    image_preview.short_description = "Preview"

class PropertyAmenityInline(admin.TabularInline):
    model = PropertyAmenity
    extra = 3
    fields = ('amenity_name', 'amenity_category')

class PropertyDocumentInline(admin.TabularInline):
    model = PropertyDocument
    extra = 0
    readonly_fields = ('uploaded_at',)
    fields = ('document_type', 'document_url', 'document_name', 'is_required_for_verification', 'uploaded_at')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'property_type', 'listing_status', 'price_per_month', 'city', 'bedrooms', 'bathrooms', 'is_verified', 'view_count', 'created_at')
    list_filter = ('property_type', 'listing_status', 'is_verified', 'is_furnished', 'pets_allowed', 'created_at', 'city')
    search_fields = ('title', 'description', 'owner__email', 'owner__full_name', 'address_line1', 'city')
    readonly_fields = ('view_count', 'created_at', 'updated_at', 'verified_at', 'primary_image_preview')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'title', 'description', 'property_type', 'listing_status')
        }),
        ('Pricing', {
            'fields': ('price_per_month', 'currency')
        }),
        ('Location', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country', 'latitude', 'longitude')
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'square_feet', 'is_furnished', 'pets_allowed', 'available_from')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verified_by', 'verified_at')
        }),
        ('Statistics', {
            'fields': ('view_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [PropertyImageInline, PropertyAmenityInline, PropertyDocumentInline]
    
    def primary_image_preview(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image_url:
            return format_html('<img src="{}" width="200" />', primary_image.image_url.url)
        return "No primary image"
    primary_image_preview.short_description = "Primary Image"
    
    actions = ['mark_as_verified', 'mark_as_active', 'mark_as_rented']
    
    def mark_as_verified(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            is_verified=True,
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} property(ies) marked as verified.')
    mark_as_verified.short_description = "Mark selected properties as verified"
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(listing_status='ACTIVE')
        self.message_user(request, f'{updated} property(ies) marked as active.')
    mark_as_active.short_description = "Mark as Active"
    
    def mark_as_rented(self, request, queryset):
        updated = queryset.update(listing_status='RENTED')
        self.message_user(request, f'{updated} property(ies) marked as rented.')
    mark_as_rented.short_description = "Mark as Rented"

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'display_order', 'is_primary', 'image_preview', 'uploaded_at')
    list_filter = ('is_primary', 'uploaded_at')
    search_fields = ('property__title', 'caption')
    readonly_fields = ('uploaded_at', 'image_preview')
    ordering = ('property', 'display_order')
    
    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="150" />', obj.image_url.url)
        return "No image"
    image_preview.short_description = "Preview"

@admin.register(PropertyAmenity)
class PropertyAmenityAdmin(admin.ModelAdmin):
    list_display = ('property', 'amenity_name', 'amenity_category')
    list_filter = ('amenity_category',)
    search_fields = ('property__title', 'amenity_name')

@admin.register(PropertyDocument)
class PropertyDocumentAdmin(admin.ModelAdmin):
    list_display = ('property', 'document_type', 'document_name', 'is_required_for_verification', 'uploaded_at')
    list_filter = ('document_type', 'is_required_for_verification', 'uploaded_at')
    search_fields = ('property__title', 'document_name')
    readonly_fields = ('uploaded_at',)

@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__email', 'user__full_name', 'property__title')
    readonly_fields = ('saved_at',)
    ordering = ('-saved_at',)

@admin.register(PropertyView)
class PropertyViewAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('property__title', 'user__email', 'ip_address')
    readonly_fields = ('viewed_at',)
    ordering = ('-viewed_at',)