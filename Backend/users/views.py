import logging

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import RegisterSerializer, LoginSerializer
from Backend.utils import create_response
from Backend.messages import response_message as mt

logger = logging.getLogger("backend")

class RegisterAPIView(APIView):
    """User registration API"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                "User registered successfully",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example=mt[201]),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
                    },
                ),
            ),
            400: openapi.Response(
                "Bad request, validation error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example=mt[400]),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
                    },
                ),
            ),
        },
        tags=["🔑 Auth"],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"new user created {serializer.data}")
            return create_response(success=True, message=mt[201], data=serializer.data, status=status.HTTP_201_CREATED)
        return create_response(success=False, message=mt[400], data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """User login API that returns JWT tokens"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                "Login successful",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example=mt[200]),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "access": openapi.Schema(type=openapi.TYPE_STRING, example="access_token_example"),
                                "refresh": openapi.Schema(type=openapi.TYPE_STRING, example="refresh_token_example"),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                "Bad request, validation error",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example=mt[400]),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
                    },
                ),
            ),
            403: openapi.Response(
                "Invalid credentials",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example=mt[403]),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
                    },
                ),
            ),
        },
        tags=["🔑 Auth"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data["username"], password=serializer.validated_data["password"])
            if user:
                refresh = RefreshToken.for_user(user)
                data = {"access": str(refresh.access_token), "refresh": str(refresh)}

                logger.info(f"user {user} logged in")
                return create_response(success=True, message=mt[200], data=data, status=status.HTTP_200_OK)

            return create_response(success=False, message=mt[403], status=status.HTTP_401_UNAUTHORIZED)

        return create_response(success=False, message=mt[400], data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """User logout API (blacklists refresh token)"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
            },
            required=["refresh"],
        ),
        responses={
            200: openapi.Response(
                "Logout successful",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example=mt[202]),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT, example=None),
                    },
                ),
            ),
            400: openapi.Response(
                "Invalid refresh token",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, example=mt[400]),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "error": openapi.Schema(type=openapi.TYPE_STRING, example="Invalid refresh token"),
                            },
                        ),
                    },
                ),
            ),
        },
        tags=["🔑 Auth"]
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"user {request.user} logged out")
            return create_response(success=True, message=mt[202], status=status.HTTP_200_OK)
        except Exception:
            logger.error(f"something happend on logging out {request.user}")
            errors = {"error": "Invalid refresh token"}
            return create_response(success=False, message=mt[400], data=errors, status=status.HTTP_400_BAD_REQUEST)
