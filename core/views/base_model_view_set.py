from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsResponsible, IsAdmin
from core.serializers import (
    AssignSerializer,
    SetOwnerSerializer,
    ActivateSerializer,
    DeactivateSerializer,
)

AUTH_USER = get_user_model()


class BaseModelViewSet(viewsets.ModelViewSet):
    ASSIGN_PERMISSIONS = [IsAuthenticated]
    ACTIVATE_PERMISSIONS = [IsAuthenticated]
    DEACTIVATE_PERMISSIONS = [IsAuthenticated]
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
        assert hasattr(obj, "responsible_user"), (
            "The object has no 'responsible_user' field!"
        )
        serializer = AssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj.responsible_user = serializer.validated_data["user_id"]
        obj.save()
        return Response({"detail": "Record assigned successfully."})

    @action(
        detail=True,
        methods=["POST"],
        url_path="activate",
        permission_classes=ACTIVATE_PERMISSIONS,
    )
    def activate(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "state"), "The object has no 'state' field!"
        assert hasattr(obj, "status"), "The object has no 'status' field!"
        serializer = ActivateSerializer(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        obj.state = 1
        obj.status = serializer.validated_data["status"]
        obj.save()
        return Response(
            {"detail": f"Record activated successfully with {obj.status} status."}
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="deactivate",
        permission_classes=DEACTIVATE_PERMISSIONS,
    )
    def deactivate(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "state"), "The object has no 'state' field!"
        assert hasattr(obj, "status"), "The object has no 'status' field!"
        serializer = DeactivateSerializer(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        obj.state = 0
        obj.status = serializer.validated_data["status"]
        obj.save()
        return Response(
            {"detail": f"Record deactivated successfully with {obj.status} status."}
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="set-owner",
        permission_classes=SET_OWNER_PERMISSIONS,
    )
    def set_owner(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "owner_user"), "The object has no 'owner_user' field!"
        serializer = SetOwnerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj.owner_user = serializer.validated_data["user_id"]
        obj.save()
        return Response({"detail": "Owner sat successfully."})

    def perform_create(self, serializer):
        model = serializer.Meta.model
        serializer.save(
            created_by=self.request.user,
            created_at=timezone.now(),
            updated_by=self.request.user,
            updated_at=timezone.now(),
            state=1,
            status=model.DEFAULT_ACTIVE_STATUS,
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user,
            updated_at=timezone.now(),
        )
