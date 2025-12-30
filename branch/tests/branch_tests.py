from fixture_tests import *

@pytest.mark.django_db
def test_branch_urls(client, test_user_token):
    """
    Test Branch endpoints.
    """
    url = reverse('branch-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 403 #will comeback

    # Test CREATE
    data = {
        "name": "Harare CBD Branch",
        "code": "HRE-001",
        "address": "Samora Machel Ave",
        "city": "Harare",
        "country": "Zimbabwe",
        "phone_number": "+26377222333"
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    assert response.status_code == 403 #will be back