from django.urls import path
from rest_framework.routers import DefaultRouter

from payrolls.views import PayrollAPIModelViewSet, TeacherPayRateAPIModelViewSet

router = DefaultRouter(use_regex_path=False)
router.register(prefix="payroll", viewset=PayrollAPIModelViewSet, basename="payroll")
router.register(
    prefix="teacher-pay-rate",
    viewset=TeacherPayRateAPIModelViewSet,
    basename="teacher-pay-rate",
)

urlpatterns = []

urlpatterns += router.urls
