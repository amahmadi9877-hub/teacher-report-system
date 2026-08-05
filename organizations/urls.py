from django.urls import path
from rest_framework.routers import DefaultRouter

from organizations.views import SchoolAPIModelViewSet

router = DefaultRouter(use_regex_path=False)
router.register(prefix="school", viewset=SchoolAPIModelViewSet, basename="school")

urlpatterns = []

urlpatterns += router.urls
