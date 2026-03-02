from django.contrib import admin
from django.utils.html import format_html
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewee', 'property', 'rating', 'review_type', 'is_verified_stay', 'created_at', 'rating_stars')
    list_filter = ('rating', 'review_type', 'is_verified_stay', 'created_at')
    search_fields = ('reviewer__email', 'reviewer__full_name', 'reviewee__email', 'reviewee__full_name', 'property__title', 'review_text')
    readonly_fields = ('created_at', 'updated_at', 'rating_stars')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Review Information', {
            'fields': ('reviewer', 'reviewee', 'property', 'review_type')
        }),
        ('Rating & Content', {
            'fields': ('rating', 'rating_stars', 'review_text', 'is_verified_stay')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span style="font-size: 18px;">{}</span>', stars)
    rating_stars.short_description = "Rating"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('reviewer', 'reviewee', 'property')