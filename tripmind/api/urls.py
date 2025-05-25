from django.urls import path
from tripmind.api.views.conversation_history_view import ConversationHistoryAPIView
from tripmind.api.views.itinerary_api_view import (
    ItineraryAPIView,
    ItineraryDetailAPIView,
    ItineraryShareAPIView,
    ItineraryShareRemoveAPIView,
    ItineraryPublicShareAPIView,
    PublicItineraryViewAPIView,
)

app_name = "tripmind"

urlpatterns = [
    path("itinerary/", ItineraryAPIView.as_view(), name="itinerary"),
    # 하위 PATH는 현재 동작을 하지 않음.
    path(
        "conversation/",
        ConversationHistoryAPIView.as_view(),
        name="conversation-history",
    ),
    path(
        "itinerary/<int:itinerary_id>/",
        ItineraryDetailAPIView.as_view(),
        name="itinerary-detail",
    ),
    path(
        "itinerary/<int:itinerary_id>/share/",
        ItineraryShareAPIView.as_view(),
        name="itinerary-share",
    ),
    path(
        "itinerary/<int:itinerary_id>/share/<int:share_id>/",
        ItineraryShareRemoveAPIView.as_view(),
        name="itinerary-share-remove",
    ),
    path(
        "itinerary/<int:itinerary_id>/public/",
        ItineraryPublicShareAPIView.as_view(),
        name="itinerary-public",
    ),
    path(
        "share/itinerary/<uuid:share_id>/",
        PublicItineraryViewAPIView.as_view(),
        name="public-itinerary",
    ),
]
