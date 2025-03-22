from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .serializers import Skill, SkillSerializer
from rest_framework.permissions import IsAdminUser
from .paginations import SkillPageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.users.versioning import CustomHeaderVersioning
from apps.users.custom_response_decorator import custom_response


@custom_response("skills")
class SkillModelViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAdminUser]
    versioning_class = CustomHeaderVersioning
    pagination_class = SkillPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'category']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['created_at']


    def create(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data)

