from django.db import models
import uuid

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('APPLICATION_RECEIVED', 'Application Received'),
        ('APPLICATION_ACCEPTED', 'Application Accepted'),
        ('APPLICATION_REJECTED', 'Application Rejected'),
        ('NEW_MESSAGE', 'New Message'),
        ('VERIFICATION_APPROVED', 'Verification Approved'),
        ('VERIFICATION_REJECTED', 'Verification Rejected'),
        ('NEW_REVIEW', 'New Review'),
        ('PROPERTY_VIEWED', 'Property Viewed'),
        ('SYSTEM', 'System Notification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional data like property_id, application_id, etc."
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Auto-update read_at when notification is marked as read
        if self.is_read and not self.read_at:
            from django.utils import timezone
            self.read_at = timezone.now()
        super().save(*args, **kwargs)
    
    def mark_as_read(self):
        """Helper method to mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.save()