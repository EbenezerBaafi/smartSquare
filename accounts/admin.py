from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'user_type', 'is_verified', 'is_email_verified', 'is_phone_verified', 'is_staff', 'created_at')
    list_filter = ('user_type', 'is_verified', 'is_email_verified', 'is_phone_verified', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'full_name', 'phone_number', 'username')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number', 'profile_picture', 'bio')}),
        ('User Type', {'fields': ('user_type',)}),
        ('Verification Status', {'fields': ('is_verified', 'is_email_verified', 'is_phone_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'user_type', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()