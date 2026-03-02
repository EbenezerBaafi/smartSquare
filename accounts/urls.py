from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView,
    UserProfileView,
    ChangePasswordView,
    VerifyEmailView,
    VerifyPhoneView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify_phone'),
]