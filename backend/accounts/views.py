from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import LoginSerializer, RegisterSerializer
from accounts.services import login_user, public_user, register_user
from core.repositories import UserRepository


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(register_user(serializer.validated_data), status=201)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(login_user(data["email"], data["password"]))


class MeView(APIView):
    def get(self, request):
        return Response(request.user.public)


class DirectoryView(APIView):
    def get(self, request):
        users = UserRepository.list_directory(exclude_id=request.user.id)
        return Response([public_user(user) for user in users])
