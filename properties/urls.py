from django.urls import path
from .views import (
    PropertyListCreateView,
    PropertyDetailView,
    MyPropertiesView,
    UploadPropertyImageView,
    DeletePropertyImageView,
    SavePropertyView,
    UnsavePropertyView,
    SavedPropertiesView
)

urlpatterns = [
    path('', PropertyListCreateView.as_view(), name='property_list_create'),
    path('<uuid:pk>/', PropertyDetailView.as_view(), name='property_detail'),
    path('my-properties/', MyPropertiesView.as_view(), name='my_properties'),
    path('<uuid:property_id>/upload-image/', UploadPropertyImageView.as_view(), name='upload_image'),
    path('image/<uuid:pk>/', DeletePropertyImageView.as_view(), name='delete_image'),
    path('<uuid:property_id>/save/', SavePropertyView.as_view(), name='save_property'),
    path('<uuid:property_id>/unsave/', UnsavePropertyView.as_view(), name='unsave_property'),
    path('saved/', SavedPropertiesView.as_view(), name='saved_properties'),
]