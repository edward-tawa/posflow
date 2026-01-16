from fixture_tests import *

# @pytest.mark.django_db
# def test_activity_log_urls(client, test_user_token):
#     """
#     Test Activity Log endpoints.
#     """
#     url = reverse('activity-log-list')
    
#     # Test GET
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     # Activity logs are typically read-only or system-generated,
#     # but we can test the filter action if defined.
#     url_filter = reverse('activity-log-filter-logs')
#     # Assuming it accepts query params or body
#     response = client.get(url_filter, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

# @pytest.mark.django_db
# def test_activity_log_filter_params(client, test_user_token):
#     """
#     Test Activity Log filtering with specific parameters (e.g., by user, date).
#     """
#     url_filter = reverse('activity-log-filter-logs')
#     # Assuming params like 'user_id' or 'date_from'
#     params = "user_id=1&date_from=2024-01-01"
#     response = client.get(f"{url_filter}?{params}", HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#####################################################################################################
#################################################################################################################

# ==========================================
# ACTIVITY LOGS
# ==========================================

# @pytest.mark.django_db
# def test_activity_log_endpoints(client, test_user_token):
#     """
#     Test Activity Log List, Detail, and Filter.
#     [Source: 37]
#     """
#     url = reverse('activity-log-list')
    
#     # Test GET
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     # Filter
#     url_filter = reverse('activity-log-filter-logs')
#     response = client.get(url_filter, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     # Detail
#     url_detail = reverse('activity-log-detail', kwargs={'pk': 1})
#     response = client.get(url_detail, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200