from rest_framework.viewsets import ModelViewSet
from .serializers import Skill, SkillSerializer
from .paginations import SkillPageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.users.versioning import CustomHeaderVersioning
from apps.users.custom_response_decorator import custom_response


@custom_response("skills")
class SkillModelViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    versioning_class = CustomHeaderVersioning
    pagination_class = SkillPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'category']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['created_at']



