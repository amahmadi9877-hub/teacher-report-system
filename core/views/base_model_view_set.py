from django.contrib.auth import get_user_model
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.decorators import prevent_inactive
from core.enums import State
from core.serializers import (
    AssignSerializer,
    SetOwnerSerializer,
    ActivateSerializer,
    DeactivateSerializer,
)

AUTH_USER = get_user_model()


class BaseModelViewSet(viewsets.ModelViewSet):
    assign_serializer_class = AssignSerializer
    activate_serializer_class = ActivateSerializer
    deactivate_serializer_class = DeactivateSerializer
    set_owner_serializer_class = SetOwnerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = None
    search_fields = []
    ordering = ["-created_on"]
    permission_classes = [IsAuthenticated]
    PERMISSIONS_BY_ACTION = {}

    def get_permissions(self):
        permission_classes = self.PERMISSIONS_BY_ACTION.get(
            self.action,
            self.permission_classes,
        )

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["POST"], url_path="assign")
    def assign(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "responsible_user"), (
            "The object has no 'responsible_user' field!"
        )
        serializer = self.assign_serializer_class(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_assign(serializer)
        return Response({"detail": "Record assigned successfully."})

    def perform_assign(self, serializer):
        obj = serializer.instance
        obj.responsible_user = serializer.validated_data["user_id"]
        obj.save()

    @action(detail=True, methods=["POST"], url_path="activate")
    def activate(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "state"), "The object has no 'state' field!"
        assert hasattr(obj, "status"), "The object has no 'status' field!"
        serializer = self.activate_serializer_class(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_activate(serializer)
        return Response(
            {"detail": f"Record activated successfully with {obj.status} status."}
        )

    def perform_activate(self, serializer):
        obj = serializer.instance
        obj.state = State.ACTIVE
        obj.status = serializer.validated_data["status"]
        obj.save()

    @action(detail=True, methods=["POST"], url_path="deactivate")
    def deactivate(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "state"), "The object has no 'state' field!"
        assert hasattr(obj, "status"), "The object has no 'status' field!"
        serializer = self.deactivate_serializer_class(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_deactivate(serializer)
        return Response(
            {"detail": f"Record deactivated successfully with {obj.status} status."}
        )

    def perform_deactivate(self, serializer):
        obj = serializer.instance
        obj.state = State.INACTIVE
        obj.status = serializer.validated_data["status"]
        obj.save()

    @action(detail=True, methods=["POST"], url_path="set-owner")
    @prevent_inactive
    def set_owner(self, request, pk):
        obj = self.get_object()
        assert hasattr(obj, "owner_user"), "The object has no 'owner_user' field!"
        serializer = self.set_owner_serializer_class(instance=obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_set_owner(serializer)
        return Response({"detail": "Owner sat successfully."})

    def perform_set_owner(self, serializer):
        obj = serializer.instance
        obj.owner_user = serializer.validated_data["user_id"]
        obj.save()

    def perform_create(self, serializer):
        model = serializer.Meta.model
        serializer.save(
            created_by=self.request.user,
            created_at=timezone.now(),
            updated_by=self.request.user,
            updated_at=timezone.now(),
            state=State.ACTIVE,
            status=model.DEFAULT_ACTIVE_STATUS,
        )

    @prevent_inactive
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user,
            updated_at=timezone.now(),
        )
