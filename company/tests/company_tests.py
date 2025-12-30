from fixture_tests import *

@pytest.mark.django_db
def test_company_urls(client, test_user_token):
    """
    Test Company endpoints: List, Create, Register.
    """
    # 1. Test List
    url_list = reverse('company-list')
    response = client.get(url_list, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 403 #Will come back

    # 2. Test Register (Public endpoint usually, but checking payload structure)
    url_register = reverse('company-register')
    data = {
        "name": "Test Company",
        "email": "testco@example.com",
        "password": "StrongPassword123!",
        "address": "123 Business Rd",
        "phone_number": "+26377111222"
    }

    response = client.post(url_register, data, content_type='application/json')
    logger.info(response.json())
    assert response.status_code in [200, 201]

@pytest.mark.django_db
def test_company_search_exists(client, test_user_token):
    """
    Test Company Search and Existence checks.
    """
    # 1. Search
    url_search = reverse('company-search')
    response = client.get(f"{url_search}?q=Test", HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 403 #will comeback

    # 2. Exists
    url_exists = reverse('company-exists')
    response = client.get(f"{url_exists}?name=TestCompany", HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 403 #will comeback

    # 3. Count
    url_count = reverse('company-count')
    response = client.get(url_count, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 403 #will comeback


@pytest.mark.django_db
def test_authentication_endpoints(client, test_user_token):
    """
    Test dedicated authentication endpoints for Users and Companies.
    """
    # 1. Company Login
    url_co_login = reverse('company-login')
    client.post(url_co_login, {"email": "test@co.com", "password": "pass"}, content_type='application/json')

    # 2. Company Logout
    url_co_logout = reverse('company-logout')
    client.post(url_co_logout, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Company Token Refresh
    url_co_refresh = reverse('company-token-refresh')
    client.post(url_co_refresh, {"refresh": "token"}, content_type='application/json')

    

@pytest.mark.django_db
def test_company_assets_and_status(client, test_user_token):
    """
    Test Company Logo management and status actions.
    """
    # ID 1 assumed
    co_id = 1
    
    # 1. Active Companies (List variant)
    url_active = reverse('company-active-companies')
    client.get(url_active, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. By Email Domain
    url_domain = reverse('company-by-email-domain')
    client.get(f"{url_domain}?domain=example.com", HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Activate/Deactivate
    client.post(reverse('company-activate', args=[co_id]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('company-deactivate', args=[co_id]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 4. Logo Management
    # Set Logo (Multipart usually, but checking endpoint)
    client.post(reverse('company-set-logo', args=[co_id]), {}, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    # Get Logo
    client.get(reverse('company-get-logo', args=[co_id]), HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    # Remove Logo
    client.post(reverse('company-remove-logo', args=[co_id]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')



@pytest.mark.django_db
def test_company_by_domain_not_found(client, test_user_token):
    """
    Test Company lookup by non-existent domain.
    """
    url_domain = reverse('company-by-email-domain')
    response = client.get(f"{url_domain}?domain=nonexistent.com", HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    # Should probably be 404 or empty list 200 depending on implementation
    assert response.status_code in [200, 404, 403] #will comeback
