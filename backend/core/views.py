from pymongo.errors import PyMongoError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.db import ping


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            ping()
        except PyMongoError:
            return Response({"status": "degraded", "database": "unavailable"}, status=503)
        return Response({"status": "ok", "database": "up"})
