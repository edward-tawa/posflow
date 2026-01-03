from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class using page number.
    - page_size: number of items per page
    - page_query_param: the query param to control page number (default ?page=1)
    - page_size_query_param: optional to let clients change page size
    - max_page_size: maximum allowed page size
    """
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'branches': data,
        })
