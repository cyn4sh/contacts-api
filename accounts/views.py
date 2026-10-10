from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.serializers import RegisterSerializer


def set_refresh_cookie(response, refresh_token):
    cookie = settings.REFRESH_COOKIE
    response.set_cookie(
        key=cookie["NAME"],
        value=refresh_token,
        max_age=cookie["MAX_AGE"],
        path=cookie["PATH"],
        secure=cookie["SECURE"],
        httponly=cookie["HTTPONLY"],
        samesite=cookie["SAMESITE"],
    )


def clear_refresh_cookie(response):
    cookie = settings.REFRESH_COOKIE
    response.delete_cookie(
        key=cookie["NAME"],
        path=cookie["PATH"],
        samesite=cookie["SAMESITE"],
    )


class AccessTokenSerializer(serializers.Serializer):
    access = serializers.CharField()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    @extend_schema(responses=AccessTokenSerializer)
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            refresh_token = response.data.pop("refresh")
            set_refresh_cookie(response, refresh_token)
        return response


class RefreshView(TokenRefreshView):
    @extend_schema(request=None, responses=AccessTokenSerializer)
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE["NAME"])
        if refresh_token is None:
            raise InvalidToken("Refresh token cookie is missing.")

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as error:
            raise InvalidToken(error.args[0])

        data = serializer.validated_data
        response = Response({"access": data["access"]}, status=status.HTTP_200_OK)
        new_refresh_token = data.get("refresh")
        if new_refresh_token:
            set_refresh_cookie(response, new_refresh_token)
        return response


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE["NAME"])
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(response)
        return response