from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                limit_str = request.query_params[self.page_size_query_param]
                limit = int(limit_str)
                if limit < 1:
                    raise ValueError
                return min(limit, self.max_page_size) if self.max_page_size else limit
            except (KeyError, ValueError):
                pass
        return self.page_size
