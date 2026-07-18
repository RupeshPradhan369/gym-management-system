from django.db import models
from apps.identity.models import User


class Conversation(models.Model):
    """
    A thread between exactly two users (member <-> trainer, or
    member <-> receptionist, etc). We enforce 'exactly two participants'
    at the application level, not via a rigid two-FK schema, so this
    could extend to group chats later without a schema change.
    """
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        usernames = ", ".join(u.username for u in self.participants.all())
        return f"Conversation: {usernames}"


class Message(models.Model):
    """A single message within a Conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.body[:30]}"