from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('TENANT', 'Tenant'),
        ('LANDLORD', 'Landlord'),
        ('BOTH', 'Both'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True, null=True)
    full_name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']
    
    def __str__(self):
        return self.email