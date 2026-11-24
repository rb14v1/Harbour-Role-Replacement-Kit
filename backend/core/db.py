import threading

from django.conf import settings
from pymongo import MongoClient

_lock = threading.Lock()
_client = None
_indexed = False


def get_client():
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                _client = MongoClient(
                    settings.MONGO_URI,
                    serverSelectionTimeoutMS=settings.MONGO_SERVER_TIMEOUT_MS,
                    tz_aware=True,
                )
    return _client


def set_client(client):
    global _client, _indexed
    _client = client
    _indexed = False


def get_db():
    global _indexed
    db = get_client()[settings.MONGO_DB_NAME]
    if not _indexed:
        db.users.create_index("email", unique=True)
        db.kits.create_index("owner_id")
        db.kits.create_index("successor_id")
        _indexed = True
    return db


def ping():
    get_client().admin.command("ping")
