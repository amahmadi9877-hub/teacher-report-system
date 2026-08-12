from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsResponsible, IsAdmin
from core.serializers import AssignSerializer

AUTH_USER = get_user_model()


class BaseModelViewSet(viewsets.ModelViewSet):
    ASSIGN_PERMISSIONS = [IsAuthenticated]
    ACTIVATE_PERMISSIONS = [IsAuthenticated]
    DEACTIVATE_PERMISSION = [IsAuthenticated]
    SET_OWNER_PERMISSIONS = [IsAuthenticated]

    # permission_classes = [IsAuthenticated]
    @action(
        detail=True,
        methods=["POST"],
        url_path="assign",
        permission_classes=ASSIGN_PERMISSIONS,
    )
    def assign(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "responsible_user"), "The object has no 'responsible_user'"
        serializer = AssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj.responsible_user = serializer.validated_data["user_id"]
        obj.save()
        return Response({"detail": "Record assigned successfully."})

    def activate(self, request):
        pass

    def deactivate(self, request):
        pass

    def set_owner(self, request):
        pass

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            created_at=timezone.now(),
            updated_by=self.request.user,
            updated_at=timezone.now(),
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user,
            updated_at=timezone.now(),
        )
