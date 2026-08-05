from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets


class BaseModelViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            created_at=timezone.now(),
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user,
            updated_at=timezone.now(),
        )
