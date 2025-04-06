from rest_framework.pagination import PageNumberPagination


class JobPostPageNumberPagination(PageNumberPagination):
    page_size = 30
    max_page_size = 200
