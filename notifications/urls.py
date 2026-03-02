from django.urls import path
from .views import (
    NotificationListView,
    UnreadNotificationsView,
    NotificationDetailView,
    MarkNotificationReadView,
    MarkAllNotificationsReadView,
    DeleteNotificationView,
    UnreadCountView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('unread/', UnreadNotificationsView.as_view(), name='unread_notifications'),
    path('<uuid:pk>/', NotificationDetailView.as_view(), name='notification_detail'),
    path('<uuid:pk>/mark-read/', MarkNotificationReadView.as_view(), name='mark_read'),
    path('mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark_all_read'),
    path('<uuid:pk>/delete/', DeleteNotificationView.as_view(), name='delete_notification'),
    path('unread-count/', UnreadCountView.as_view(), name='unread_count'),
]