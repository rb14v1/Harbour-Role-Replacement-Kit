import mongomock
from django.test import SimpleTestCase
from rest_framework.test import APIClient

from core import db

PASSWORD = "StrongPass123"


class ApiTestCase(SimpleTestCase):
    def setUp(self):
        db.set_client(mongomock.MongoClient())
        self.api = APIClient()

    def tearDown(self):
        db.set_client(None)
        self.api.credentials()

    def register(self, email, full_name="Test User", department="Marketing", designation="Marketing Executive"):
        return self.api.post(
            "/api/auth/register/",
            {
                "full_name": full_name,
                "email": email,
                "department": department,
                "designation": designation,
                "password": PASSWORD,
            },
            format="json",
        )

    def login(self, email):
        response = self.api.post("/api/auth/login/", {"email": email, "password": PASSWORD}, format="json")
        self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['token']}")
        return response
