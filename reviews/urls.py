from django.urls import path
from .views import (
    CreateReviewView,
    PropertyReviewsView,
    UserReviewsView,
    MyReviewsView,
    ReviewDetailView,
    PropertyAverageRatingView,
    UserAverageRatingView
)

urlpatterns = [
    path('create/', CreateReviewView.as_view(), name='create_review'),
    path('property/<uuid:property_id>/', PropertyReviewsView.as_view(), name='property_reviews'),
    path('user/<uuid:user_id>/', UserReviewsView.as_view(), name='user_reviews'),
    path('my-reviews/', MyReviewsView.as_view(), name='my_reviews'),
    path('<uuid:pk>/', ReviewDetailView.as_view(), name='review_detail'),
    path('property/<uuid:property_id>/average/', PropertyAverageRatingView.as_view(), name='property_average_rating'),
    path('user/<uuid:user_id>/average/', UserAverageRatingView.as_view(), name='user_average_rating'),
]