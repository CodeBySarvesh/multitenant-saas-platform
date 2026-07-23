from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from apps.common.serializers import MessageSerializer
from apps.accounts.serializers import LoginSerializer, LogoutSerializer, RegisterResponseSerializer, RegisterSerializer, TokenSerializer, UserListSerializer
from .models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

# class RegisterView(APIView):

#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")
#         name = request.data.get("name")

#         if not email or not password:
#             return Response({"error": "Email & password required"}, status=400)
        
#         if User.objects.filter(email=email).exists():
#             return Response({"error": "User already exists"}, status=400)

#         user = User.objects.create_user(
#             email=email,
#             password=password,
#             name=name
#         )

#         return Response({"message": "User created"}, status=201)

class RegisterView(APIView):

    @extend_schema(
        request=RegisterSerializer,
        responses={
            201: RegisterResponseSerializer,
            400: None,
        },
        summary="Register a new user",
        description="Creates a new user account.",
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        name = serializer.validated_data["name"]

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "User already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User.objects.create_user(
            email=email,
            password=password,
            name=name,
        )

        return Response(
            {"message": "User created"},
            status=status.HTTP_201_CREATED,
        )

# class LoginView(APIView):

#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")

#         user = authenticate(email=email, password=password)

#         if not user:
#             return Response({"error": "Invalid credentials"}, status=401)

#         refresh = RefreshToken.for_user(user)

#         return Response({
#             "access": str(refresh.access_token),
#             "refresh": str(refresh)
#         })

class LoginView(APIView):

    @extend_schema(
        request=LoginSerializer,
        responses={200: TokenSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(email=email, password=password)

        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)

        return Response({
            "user_id" : user.id,
            "name" : user.name,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })
    
class UserListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]  
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserListSerializer

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={
            205: MessageSerializer,
            400: MessageSerializer,
        },
        summary="Logout user",
        description="Blacklist the refresh token to logout the user.",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except Exception:
            return Response(
                {"message": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Successfully logged out."},
            status=status.HTTP_205_RESET_CONTENT,
        )