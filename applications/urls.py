from django.urls import path
from .views import (
    SubmitApplicationView,
    MyApplicationsView,
    PropertyApplicationsView,
    ApplicationDetailView,
    RespondToApplicationView,
    WithdrawApplicationView,
    ReceivedApplicationsView
)

urlpatterns = [
    path('submit/', SubmitApplicationView.as_view(), name='submit_application'),
    path('my-applications/', MyApplicationsView.as_view(), name='my_applications'),
    path('property/<uuid:property_id>/', PropertyApplicationsView.as_view(), name='property_applications'),
    path('<uuid:pk>/', ApplicationDetailView.as_view(), name='application_detail'),
    path('<uuid:pk>/respond/', RespondToApplicationView.as_view(), name='respond_application'),
    path('<uuid:pk>/withdraw/', WithdrawApplicationView.as_view(), name='withdraw_application'),
    path('received/', ReceivedApplicationsView.as_view(), name='received_applications'),
]