from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer
)
from .models import User

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Register a new user
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """
    POST /api/auth/login/
    Login user and return JWT tokens
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Update last login
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Logout user by blacklisting refresh token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET /api/auth/profile/
    PUT /api/auth/profile/
    Get or update user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH':
            return UserProfileUpdateSerializer
        return UserSerializer

class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/
    Change user password
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

class VerifyEmailView(APIView):
    """
    POST /api/auth/verify-email/
    Verify user email (simplified version)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # In production, you'd verify a token sent via email
        # For now, we'll just mark as verified
        user = request.user
        user.is_email_verified = True
        user.save()
        
        return Response({
            'message': 'Email verified successfully'
        }, status=status.HTTP_200_OK)

class VerifyPhoneView(APIView):
    """
    POST /api/auth/verify-phone/
    Verify user phone number (simplified version)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # In production, you'd verify an OTP sent via SMS
        # For now, we'll just mark as verified
        user = request.user
        user.is_phone_verified = True
        user.save()
        
        return Response({
            'message': 'Phone verified successfully'
        }, status=status.HTTP_200_OK)