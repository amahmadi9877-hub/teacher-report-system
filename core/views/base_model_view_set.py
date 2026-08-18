from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.serializers import (
    AssignSerializer,
    SetOwnerSerializer,
    ActivateSerializer,
    DeactivateSerializer,
)

AUTH_USER = get_user_model()


class BaseModelViewSet(viewsets.ModelViewSet):
    set_owner_serializer_class = SetOwnerSerializer
    assign_serializer_class = AssignSerializer
    permission_classes = [IsAuthenticated]
    PERMISSIONS_BY_ACTION = {}

    def get_permissions(self):
        permission_classes = self.PERMISSIONS_BY_ACTION.get(
            self.action,
            self.permission_classes,
        )

        return [permission() for permission in permission_classes]

    @action(
        detail=True,
        methods=["POST"],
        url_path="assign",
    )
    def assign(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "responsible_user"), (
            "The object has no 'responsible_user' field!"
        )
        serializer = self.assign_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj.responsible_user = serializer.validated_data["user_id"]
        obj.save()
        return Response({"detail": "Record assigned successfully."})

    @action(
        detail=True,
        methods=["POST"],
        url_path="activate",
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
    )
    def set_owner(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "owner_user"), "The object has no 'owner_user' field!"
        serializer = self.set_owner_serializer_class(data=request.data)
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
