from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from core.exceptions import AppError
from core.repositories import UserRepository
from core.security import create_token, hash_password, verify_password

EMAIL_TAKEN_MESSAGE = "An account with this email already exists."


def public_user(document):
    return {
        "id": str(document["_id"]),
        "full_name": document["full_name"],
        "email": document["email"],
        "department": document["department"],
        "designation": document["designation"],
    }


def _session(document):
    user = public_user(document)
    return {"token": create_token(user["id"], user["email"]), "user": user}


def register_user(data):
    email = data["email"].strip().lower()
    if UserRepository.find_by_email(email):
        raise AppError(EMAIL_TAKEN_MESSAGE, "email_taken", 409)
    document = {
        "full_name": data["full_name"],
        "email": email,
        "department": data["department"],
        "designation": data["designation"],
        "password_hash": hash_password(data["password"]),
        "created_at": datetime.now(timezone.utc),
    }
    try:
        UserRepository.create(document)
    except DuplicateKeyError as exc:
        raise AppError(EMAIL_TAKEN_MESSAGE, "email_taken", 409) from exc
    return _session(document)


def login_user(email, password):
    document = UserRepository.find_by_email(email.strip().lower())
    if document is None or not verify_password(password, document["password_hash"]):
        raise AppError("Invalid email or password.", "invalid_credentials", 401)
    return _session(document)
