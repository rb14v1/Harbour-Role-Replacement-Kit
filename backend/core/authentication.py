import jwt
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from accounts.services import public_user
from core.repositories import UserRepository
from core.security import decode_token


class AuthenticatedUser:
    is_authenticated = True
    is_anonymous = False

    def __init__(self, document):
        self.public = public_user(document)
        self.id = self.public["id"]

    def __str__(self):
        return self.public["full_name"]


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("latin-1")
        if not header:
            return None
        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed("Authorization header must be in the form 'Bearer <token>'.")
        token = parts[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationFailed("Your session has expired. Please log in again.") from exc
        except jwt.PyJWTError as exc:
            raise AuthenticationFailed("Invalid session token. Please log in again.") from exc
        document = UserRepository.find_by_id(payload.get("sub"))
        if document is None:
            raise AuthenticationFailed("This account no longer exists.")
        return AuthenticatedUser(document), token

    def authenticate_header(self, request):
        return "Bearer"
