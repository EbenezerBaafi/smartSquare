from django.db import models
import uuid

class PropertyApplication(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='applications')
    tenant = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    message = models.TextField(help_text="Message from tenant to landlord")
    landlord_response = models.TextField(blank=True, help_text="Response from landlord")
    move_in_date = models.DateField()
    lease_duration_months = models.IntegerField(help_text="Duration of lease in months")
    applied_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['property', 'tenant', 'status']  # Prevent duplicate active applications
    
    def __str__(self):
        return f"{self.tenant.full_name} -> {self.property.title} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-update responded_at when status changes from PENDING
        if self.pk:
            old_instance = PropertyApplication.objects.get(pk=self.pk)
            if old_instance.status == 'PENDING' and self.status != 'PENDING':
                from django.utils import timezone
                self.responded_at = timezone.now()
        super().save(*args, **kwargs)