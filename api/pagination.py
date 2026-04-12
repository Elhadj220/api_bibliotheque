"""
Classes de pagination
"""
from rest_framework.pagination import PageNumberPagination, CursorPagination


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100
    page_query_param = 'page'


class PerformantePagination(CursorPagination):
    """Pour les grandes collections, plus performant"""
    page_size = 10
    ordering = '-date_creation'
