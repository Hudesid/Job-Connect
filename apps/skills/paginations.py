from rest_framework.pagination import PageNumberPagination


class SkillPageNumberPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100