from django.contrib import admin
from tripmind.models.session import ConversationSession, ConversationMessage
from tripmind.models.itinerary import Itinerary


@admin.register(ConversationSession)
class ConversationSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "user", "created_at", "updated_at")
    search_fields = ("session_id", "user__username")


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "content", "created_at")
    list_filter = ("role",)
    search_fields = ("content",)


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ("title", "destination", "duration", "user", "date", "created_at")
    list_filter = ("destination", "share_type", "date")
    search_fields = ("title", "destination")
