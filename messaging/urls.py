from django.urls import path
from .views import (
    ConversationListView,
    ConversationDetailView,
    StartConversationView,
    SendMessageView,
    UnreadMessagesCountView,
    MarkMessageAsReadView,
    DeleteConversationView
)

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<uuid:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('start/', StartConversationView.as_view(), name='start_conversation'),
    path('send/', SendMessageView.as_view(), name='send_message'),
    path('unread-count/', UnreadMessagesCountView.as_view(), name='unread_count'),
    path('message/<uuid:pk>/mark-read/', MarkMessageAsReadView.as_view(), name='mark_read'),
    path('conversations/<uuid:pk>/delete/', DeleteConversationView.as_view(), name='delete_conversation'),
]