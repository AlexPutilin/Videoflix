from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class Cookies:
    @staticmethod
    def set_token_cookies(response, token_data):
        response.set_cookie(
            key="access_token",
            value=token_data["access"],
            httponly=True,
            secure=False,
            samesite="Lax",
        )
        response.set_cookie(
            key="refresh_token",
            value=token_data["refresh"],
            httponly=True,
            secure=False,
            samesite="Lax",
        )

    @staticmethod
    def set_access_cookie(response, access_token):
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
        )

    @staticmethod
    def delete_token_cookies(response):
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

    @staticmethod
    def blacklist_refresh_token(refresh_token):
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            pass