from django.contrib import admin
from django.utils.html import format_html
from .models import PropertyOwnerVerification, VerificationDocument

class VerificationDocumentInline(admin.TabularInline):
    model = VerificationDocument
    extra = 0
    readonly_fields = ('document_name', 'file_size', 'uploaded_at', 'view_document')
    fields = ('document_type', 'view_document', 'document_name', 'file_size', 'uploaded_at')
    can_delete = False
    
    def view_document(self, obj):
        if obj.document_url:
            return format_html('<a href="{}" target="_blank">View Document</a>', obj.document_url.url)
        return "No document"
    view_document.short_description = "Document"

@admin.register(PropertyOwnerVerification)
class PropertyOwnerVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_type', 'status', 'submitted_at', 'verified_at', 'verified_by', 'view_documents')
    list_filter = ('status', 'verification_type', 'submitted_at', 'verified_at')
    search_fields = ('user__email', 'user__full_name', 'user__phone_number')
    readonly_fields = ('submitted_at', 'created_at', 'updated_at')
    ordering = ('-submitted_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Verification Details', {
            'fields': ('verification_type', 'status', 'rejection_reason')
        }),
        ('Review Information', {
            'fields': ('verified_by', 'verified_at', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [VerificationDocumentInline]
    
    def view_documents(self, obj):
        count = obj.documents.count()
        return format_html('{} document(s)', count)
    view_documents.short_description = "Documents"
    
    def save_model(self, request, obj, form, change):
        # Auto-set verified_by when approving
        if obj.status == 'APPROVED' and not obj.verified_by:
            obj.verified_by = request.user
            from django.utils import timezone
            obj.verified_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    actions = ['approve_verification', 'reject_verification']
    
    def approve_verification(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='APPROVED',
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} verification(s) approved successfully.')
    approve_verification.short_description = "Approve selected verifications"
    
    def reject_verification(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            status='REJECTED',
            verified_by=request.user,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} verification(s) rejected.')
    reject_verification.short_description = "Reject selected verifications"

@admin.register(VerificationDocument)
class VerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ('verification', 'document_type', 'document_name', 'file_size', 'uploaded_at', 'view_document')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('verification__user__email', 'document_name', 'document_type')
    readonly_fields = ('uploaded_at', 'view_document')
    ordering = ('-uploaded_at',)
    
    def view_document(self, obj):
        if obj.document_url:
            return format_html('<a href="{}" target="_blank">View Document</a>', obj.document_url.url)
        return "No document"
    view_document.short_description = "Document Link"