from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import AppError
from core.repositories import KitRepository
from transitions import services
from transitions.presenters import present_kit, present_summary
from transitions.serializers import (
    KitCreateSerializer,
    KitUpdateSerializer,
    PlaybookGenerateSerializer,
    ProgressSerializer,
    ThreadMessageSerializer,
)


def _validated(serializer_class, data):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class KitListCreateView(APIView):
    def get(self, request):
        role = request.query_params.get("role", "owner")
        if role not in ("owner", "successor"):
            raise AppError("The role query parameter must be 'owner' or 'successor'.", "invalid_role", 400)
        kits = KitRepository.list_for_user(request.user.id, role)
        return Response([present_summary(kit, request.user.id) for kit in kits])

    def post(self, request):
        data = _validated(KitCreateSerializer, request.data)
        kit = services.create_kit(request.user, data)
        return Response(present_kit(kit, request.user.id), status=201)


class PlaybookGenerateView(APIView):
    def post(self, request):
        data = _validated(PlaybookGenerateSerializer, request.data)
        items = services.generate_playbook(data["role_title"], data["raw_notes"])
        return Response({"items": items})


class KitDetailView(APIView):
    def get(self, request, kit_id):
        kit = services.load_party_kit(kit_id, request.user)
        return Response(present_kit(kit, request.user.id))

    def patch(self, request, kit_id):
        data = _validated(KitUpdateSerializer, request.data)
        kit = services.load_party_kit(kit_id, request.user)
        updated = services.update_playbook(kit, request.user, data)
        return Response(present_kit(updated, request.user.id))


class ItemProgressView(APIView):
    def post(self, request, kit_id, item_id):
        data = _validated(ProgressSerializer, request.data)
        kit = services.load_party_kit(kit_id, request.user)
        updated = services.update_progress(kit, request.user, item_id, data["progress"])
        return Response(present_kit(updated, request.user.id))


class ItemThreadView(APIView):
    def post(self, request, kit_id, item_id):
        data = _validated(ThreadMessageSerializer, request.data)
        kit = services.load_party_kit(kit_id, request.user)
        updated = services.post_message(kit, request.user, item_id, data["text"])
        return Response(present_kit(updated, request.user.id), status=201)


class ReadinessCheckView(APIView):
    def post(self, request, kit_id):
        kit = services.load_party_kit(kit_id, request.user)
        updated = services.run_readiness_check(kit, request.user)
        return Response(present_kit(updated, request.user.id))


class SignOffView(APIView):
    def post(self, request, kit_id):
        kit = services.load_party_kit(kit_id, request.user)
        updated = services.sign_off(kit, request.user)
        return Response(present_kit(updated, request.user.id))
