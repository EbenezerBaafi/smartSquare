from django.db import models
import uuid

class PropertyOwnerVerification(models.Model):
    VERIFICATION_TYPE_CHOICES = [
        ('ID_CARD', 'ID Card'),
        ('PASSPORT', 'Passport'),
        ('UTILITY_BILL', 'Utility Bill'),
        ('TITLE_DEED', 'Title Deed'),
        ('LAND_CERTIFICATE', 'Land Certificate'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='verifications')
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True)
    verified_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='verified_users')
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.verification_type} - {self.status}"

class VerificationDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verification = models.ForeignKey(PropertyOwnerVerification, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50)
    document_url = models.FileField(upload_to='verification_docs/')
    document_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document_type} - {self.document_name}"