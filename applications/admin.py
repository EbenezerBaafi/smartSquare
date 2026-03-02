from django.contrib import admin
from django.utils.html import format_html
from .models import PropertyApplication

@admin.register(PropertyApplication)
class PropertyApplicationAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property', 'status', 'move_in_date', 'lease_duration_months', 'applied_at', 'responded_at')
    list_filter = ('status', 'applied_at', 'move_in_date')
    search_fields = ('tenant__email', 'tenant__full_name', 'property__title', 'message')
    readonly_fields = ('applied_at', 'responded_at', 'created_at', 'updated_at')
    ordering = ('-applied_at',)
    
    fieldsets = (
        ('Application Details', {
            'fields': ('property', 'tenant', 'status')
        }),
        ('Lease Information', {
            'fields': ('move_in_date', 'lease_duration_months')
        }),
        ('Messages', {
            'fields': ('message', 'landlord_response')
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'responded_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['accept_application', 'reject_application']
    
    def accept_application(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='PENDING').update(
            status='ACCEPTED',
            responded_at=timezone.now()
        )
        self.message_user(request, f'{updated} application(s) accepted.')
    accept_application.short_description = "Accept selected applications"
    
    def reject_application(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(status='PENDING').update(
            status='REJECTED',
            responded_at=timezone.now()
        )
        self.message_user(request, f'{updated} application(s) rejected.')
    reject_application.short_description = "Reject selected applications"