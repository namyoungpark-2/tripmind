from django.db import models
from django.contrib.auth.models import User


class ConversationSession(models.Model):
    """사용자 대화 세션"""

    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session_id


class ConversationMessage(models.Model):
    """대화 메시지"""

    session = models.ForeignKey(
        ConversationSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20)  # user 또는 assistant
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
