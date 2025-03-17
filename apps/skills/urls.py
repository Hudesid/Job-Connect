from rest_framework.routers import DefaultRouter
from .views import SkillModelViewSet

router = DefaultRouter()

router.register(r"skills", SkillModelViewSet)

urlpatterns = router.urls