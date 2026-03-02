from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'receiver', 'sent_at', 'is_read', 'read_at')
    fields = ('sender', 'receiver', 'message_content', 'is_read', 'sent_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'get_participants', 'last_message_at', 'created_at', 'message_count')
    list_filter = ('created_at', 'last_message_at')
    search_fields = ('property__title', 'participants__email', 'participants__full_name')
    readonly_fields = ('created_at', 'last_message_at')
    filter_horizontal = ('participants',)
    ordering = ('-last_message_at',)
    
    inlines = [MessageInline]
    
    def get_participants(self, obj):
        return ", ".join([p.full_name for p in obj.participants.all()])
    get_participants.short_description = "Participants"
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'conversation', 'is_read', 'sent_at', 'message_preview')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__email', 'sender__full_name', 'receiver__email', 'receiver__full_name', 'message_content')
    readonly_fields = ('sent_at', 'read_at')
    ordering = ('-sent_at',)
    
    fieldsets = (
        ('Conversation', {
            'fields': ('conversation',)
        }),
        ('Participants', {
            'fields': ('sender', 'receiver')
        }),
        ('Message', {
            'fields': ('message_content',)
        }),
        ('Status', {
            'fields': ('is_read', 'read_at', 'sent_at')
        }),
    )
    
    def message_preview(self, obj):
        return obj.message_content[:50] + "..." if len(obj.message_content) > 50 else obj.message_content
    message_preview.short_description = "Preview"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('sender', 'receiver', 'conversation')