from django.db import models
import uuid

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    participants = models.ManyToManyField('accounts.User', related_name='conversations')
    last_message_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-last_message_at']
    
    def __str__(self):
        participant_names = ", ".join([p.full_name for p in self.participants.all()[:2]])
        return f"Conversation: {participant_names}"
    
    def get_other_participant(self, user):
        """Get the other participant in a 2-person conversation"""
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='received_messages')
    message_content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sent_at']
    
    def __str__(self):
        return f"{self.sender.full_name} to {self.receiver.full_name}: {self.message_content[:50]}"
    
    def save(self, *args, **kwargs):
        # Auto-update read_at when message is marked as read
        if self.is_read and not self.read_at:
            from django.utils import timezone
            self.read_at = timezone.now()
        super().save(*args, **kwargs)
        
        # Update conversation's last_message_at
        self.conversation.save()  # This triggers auto_now on last_message_at