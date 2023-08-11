"""rest_framework_settings.py
Some overrides related to rest-framework."""
from rest_framework.pagination import PageNumberPagination
import os

PAGE_SIZE = int(os.environ.get("API_PAGE_SIZE", 31))


class PaginationSettings(PageNumberPagination):
    """To allow the client to override the page size,
    we have to specify a custom class."""

    page_size = PAGE_SIZE
    page_size_query_param = os.environ.get("API_PAGE_QUERY_PARAM", "limit")
    max_page_size = int(os.environ.get("API_MAX_PAGE_SIZE", 31))
