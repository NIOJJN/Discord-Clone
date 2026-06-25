# chat/models.py
from django.db import models
from accounts.models import User
from servers.models import Channel

class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    attachments = models.FileField(upload_to='attachments/', blank=True, null=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_dms')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_dms')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachments = models.FileField(upload_to='dm_attachments/', blank=True, null=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"DM from {self.sender.username} to {self.recipient.username}"

class VoiceChannel(models.Model):
    channel = models.OneToOneField(Channel, on_delete=models.CASCADE, related_name='voice_channel')
    connected_users = models.ManyToManyField(User, related_name='voice_connections', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def user_count(self):
        return self.connected_users.count()