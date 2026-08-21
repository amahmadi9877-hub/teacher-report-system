from django.urls import path
from rest_framework.routers import DefaultRouter

from reports.views import SessionReportAPIModelViewSet

router = DefaultRouter(use_regex_path=False)
router.register(
    prefix="session-report",
    viewset=SessionReportAPIModelViewSet,
    basename="session-report",
)

urlpatterns = []

urlpatterns += router.urls
