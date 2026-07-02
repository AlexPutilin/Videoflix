from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import RegisterSerializer, LoginSerializer, PasswordResetSerializer, PasswordConfirmSerializer
from app_auth.services.cookies_service import Cookies
from app_auth.services.mail_service import send_activation_email, send_password_reset_email


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            send_activation_email(user, token)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        user = get_user_from_uid(uidb64)
        if not user or not default_token_generator.check_token(user, token):
            return Response({"detail": "Activation failed"}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save(update_fields=["is_active"])
        return Response({"message": "Account successfully activated"}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = Response(status=status.HTTP_200_OK)
        Cookies.set_token_cookies(response, serializer.validated_data)
        return response
    

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST)
        response = Response({"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)
        Cookies.blacklist_refresh_token(refresh_token)
        Cookies.delete_token_cookies(response)
        return response


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"detail": "Refresh token is missing."}, status=status.HTTP_400_BAD_REQUEST,)
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except TokenError:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)
        response = Response({"detail": "Token refreshed", "access": access_token}, status=status.HTTP_200_OK)
        Cookies.set_access_cookie(response, access_token)
        return response


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(username=email, is_active=True).first()
        if user:
            token = default_token_generator.make_token(user)
            send_password_reset_email(user, token)
        return Response({"detail": "An email has been sent to reset your password."}, status=status.HTTP_200_OK)


class PasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_user_from_uid(uidb64)
        if not user or not default_token_generator.check_token(user, token):
            return Response({"detail": "Password reset failed."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK)


def get_user_from_uid(uidb64):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        return user
    except Exception:
        return None