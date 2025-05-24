from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from datetime import timedelta


class Itinerary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="itineraries")
    title = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    duration = models.CharField(max_length=100)
    travelers = models.PositiveIntegerField(default=1)
    budget = models.CharField(max_length=100, blank=True)
    preferences = models.TextField(blank=True)
    special_requirements = models.TextField(blank=True)
    itinerary_plan = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    share_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_public = models.BooleanField(default=False)
    share_expires_at = models.DateTimeField(null=True, blank=True)

    SHARE_TYPE_CHOICES = [
        ("NONE", "공유 안함"),
        ("VIEW", "읽기 전용"),
        ("EDIT", "편집 가능"),
    ]
    share_type = models.CharField(
        max_length=10, choices=SHARE_TYPE_CHOICES, default="NONE"
    )

    def __str__(self):
        return f"{self.destination} - {self.duration}"

    def get_share_url(self):
        return f"/itinerary/share/{self.share_id}"

    def create_share_link(self, days=7, share_type="VIEW"):
        self.is_public = True
        self.share_type = share_type
        self.share_expires_at = timezone.now() + timedelta(days=days)
        self.save()
        return self.get_share_url()

    def is_share_valid(self):
        if not self.is_public:
            return False

        if self.share_expires_at and self.share_expires_at < timezone.now():
            return False

        return True

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Itineraries"


class SharedItinerary(models.Model):
    itinerary = models.ForeignKey(
        Itinerary, on_delete=models.CASCADE, related_name="shared_with"
    )
    shared_with = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shared_itineraries"
    )
    can_edit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("itinerary", "shared_with")
        verbose_name_plural = "Shared Itineraries"

    def __str__(self):
        return f"{self.itinerary.title} - 공유됨: {self.shared_with.username}"
