from django.urls import path
from .views import (
    SubmitVerificationView,
    UploadVerificationDocumentView,
    MyVerificationsView,
    VerificationDetailView,
    PendingVerificationsView,
    ReviewVerificationView,
    DeleteVerificationDocumentView
)

urlpatterns = [
    path('submit/', SubmitVerificationView.as_view(), name='submit_verification'),
    path('<uuid:verification_id>/upload-document/', UploadVerificationDocumentView.as_view(), name='upload_document'),
    path('my-verifications/', MyVerificationsView.as_view(), name='my_verifications'),
    path('<uuid:pk>/', VerificationDetailView.as_view(), name='verification_detail'),
    path('pending/', PendingVerificationsView.as_view(), name='pending_verifications'),
    path('<uuid:pk>/review/', ReviewVerificationView.as_view(), name='review_verification'),
    path('document/<uuid:pk>/', DeleteVerificationDocumentView.as_view(), name='delete_document'),
]