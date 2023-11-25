from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from typing import Optional


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that extends PageNumberPagination.
    Allows clients to control the page size using a query parameter.
    """
    page_size = 6
    page_size_query_param = "limit"
    max_page_size = 100

    def get_page_size(self, request: Request) -> Optional[int]:
        """
        Determine the page size for pagination.

        Args:
            request (Request): The incoming request.

        Returns:
            Optional[int]: The page size to be used for pagination.
                           Returns None if the page size is not set.
        """
        if self.page_size_query_param:
            try:
                limit_str = request.query_params.get(
                    self.page_size_query_param, ""
                )
                limit = int(limit_str)
                if limit < 1:
                    raise ValueError
                return min(limit, self.max_page_size) \
                    if self.max_page_size else limit
            except (KeyError, ValueError):
                pass
        return self.page_size
