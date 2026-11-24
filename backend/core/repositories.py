from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument

from core.db import get_db


def to_object_id(value):
    if value is None:
        return None
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


class UserRepository:
    @staticmethod
    def _collection():
        return get_db().users

    @classmethod
    def create(cls, document):
        cls._collection().insert_one(document)
        return document

    @classmethod
    def find_by_email(cls, email):
        return cls._collection().find_one({"email": email})

    @classmethod
    def find_by_id(cls, user_id):
        oid = to_object_id(user_id)
        if oid is None:
            return None
        return cls._collection().find_one({"_id": oid})

    @classmethod
    def list_directory(cls, exclude_id=None):
        query = {}
        oid = to_object_id(exclude_id)
        if oid is not None:
            query["_id"] = {"$ne": oid}
        cursor = cls._collection().find(query, {"password_hash": 0}).sort([("department", 1), ("full_name", 1)])
        return list(cursor)


class KitRepository:
    @staticmethod
    def _collection():
        return get_db().kits

    @classmethod
    def create(cls, document):
        cls._collection().insert_one(document)
        return document

    @classmethod
    def find_by_id(cls, kit_id):
        oid = to_object_id(kit_id)
        if oid is None:
            return None
        return cls._collection().find_one({"_id": oid})

    @classmethod
    def list_for_user(cls, user_id, role):
        field = "owner_id" if role == "owner" else "successor_id"
        return list(cls._collection().find({field: user_id}).sort("created_at", -1))

    @classmethod
    def update(cls, kit_id, fields):
        oid = to_object_id(kit_id)
        if oid is None:
            return None
        return cls._collection().find_one_and_update(
            {"_id": oid},
            {"$set": fields},
            return_document=ReturnDocument.AFTER,
        )
