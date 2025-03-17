from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .serializers import Skill, SkillSerializer
from rest_framework.permissions import IsAdminUser
from .paginations import SkillPageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter


class SkillModelViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAdminUser]
    pagination_class = SkillPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'category']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['created_at']


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            skill = serializer.save()
            return Response({
                "status": True,
                "message": "Ko'nikma muvaffaqiyatli qo'shildi.",
                "data": {skill}
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                "status": False,
                "error": "Noto'g'ri ma'lumot kiritlgan.",
            }, status=status.HTTP_400_BAD_REQUEST)


