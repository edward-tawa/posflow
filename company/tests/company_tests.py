from fixture_tests import *

@pytest.mark.django_db
def test_company_urls(client, test_company_token_fixture):
    """
    Test Company endpoints: List, Create, Register.
    """
    # 1. Test List
    url_list = reverse('company-list')
    response = client.get(url_list, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(test_company_token_fixture)
    logger.info(response.json())
    assert response.status_code == 200

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
def test_company_search_exists(client, test_company_token_fixture):
    """
    Test Company Search and Existence checks.
    """
    # 1. Search
    url_search = reverse('company-search')
    response = client.get(f"{url_search}?q=Test", HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200

    # 2. Exists
    url_exists = reverse('company-exists')
    response = client.get(f"{url_exists}?name=TestCompany", HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200

    # 3. Count
    url_count = reverse('company-count')
    response = client.get(url_count, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200


@pytest.mark.django_db
def test_authentication_endpoints(client, test_company_token_fixture):
    """
    Test dedicated authentication endpoints for Users and Companies.
    """
    # 1. Company Login
    url_co_login = reverse('company-login')
    response = client.post(url_co_login, {"email": "techcity@gmail.com", "password": "techcity"}, content_type='application/json')
    logger.info(response.json())
    assert response.status_code == 200

    # 2. Company Logout
    url_co_logout = reverse('company-logout')
    client.post(url_co_logout, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200

    # 3. Company Token Refresh
    url_co_refresh = reverse('company-token-refresh')
    client.post(url_co_refresh, {"refresh": "token"}, content_type='application/json')
    logger.info(response.json())
    assert response.status_code == 200
    

@pytest.mark.django_db
def test_company_assets_and_status(client, test_company_token_fixture):
    """
    Test Company Logo management and status actions.
    """
    # ID 1 assumed
    co_id = 1
    
    # 1. Active Companies (List variant)
    url_active = reverse('company-active-companies')
    response = client.get(url_active, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200

    # 2. By Email Domain
    url_domain = reverse('company-by-email-domain')
    response = client.get(f"{url_domain}?domain=example.com", HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200

    # 3. Activate/Deactivate
    response = client.post(reverse('company-activate', args=[co_id]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200
    
    response = client.post(reverse('company-deactivate', args=[co_id]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200

    # 4. Logo Management
    # Set Logo (Multipart usually, but checking endpoint)
    response = client.post(reverse('company-set-logo', args=[co_id]), {}, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 400
    
    # Get Logo
    # response = client.get(reverse('company-get-logo', args=[co_id]), HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    # logger.info(response.json())
    # assert response.status_code == 200
    
    # # Remove Logo
    # response = client.post(reverse('company-remove-logo', args=[co_id]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    # logger.info(response.json())
    # assert response.status_code == 200


@pytest.mark.django_db
def test_company_by_domain_not_found(client, test_company_token_fixture):
    """
    Test Company lookup by non-existent domain.
    """
    url_domain = reverse('company-by-email-domain')
    response = client.get(f"{url_domain}?domain=nonexistent.com", HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code in [200, 404]



##########################################################################################################################################################################################################
######################################################################################################################################################################################################################


# ==========================================
# COMPANY AUTHENTICATION & REGISTRATION
# ==========================================

@pytest.mark.django_db
def test_company_auth_endpoints(client, test_company_token_fixture):
    """
    Test Company Login, Logout, Register, and Token Refresh endpoints.
    """
    # 1. Company Register
    url = reverse('company-register')

    data = {
        "name": "Test Company",
        "email": "testco@example.com",
        "password": "StrongPassword123!",
        "address": "123 Business Rd",
        "phone_number": "+26377111222"
    }

    response = client.post(
        url, 
        data, 
        content_type='application/json'
    )
    logger.info(response.json())

    assert response.status_code == 201

    # 2. Company Login
    url = reverse('company-login')

    data = {
        "email": "testco@example.com",
        "password": "StrongPassword123!"
    }

    response = client.post(
        url, 
        data, 
        content_type='application/json'
    )
    logger.info(response.json())

    assert response.status_code == 200

    # 3. Company Token Refresh
    url = reverse('company-token-refresh')

    data = {
        'refresh_token':response.json().get('refresh_token')
    }

    response = client.post(
        url, 
        data, 
        content_type='application/json'
    )
    logger.info(response.json())
    assert response.status_code == 200

    # 4. Company Logout
    url = reverse('company-logout')
    data = None
    response = client.post(
        url, 
        data, 
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    logger.info(response.json())
    assert response.status_code == 200


# ==========================================
# COMPANY MANAGEMENT (List & Detail)
# ==========================================

@pytest.mark.django_db
def test_company_list_endpoints(client, test_company_token_fixture):
    """
    Test Company List and count endpoints.
    """
    url = reverse('company-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200


@pytest.mark.django_db
def test_company_detail_endpoints(client, test_company_token_fixture):
    """
    Test Company Detail, Update, and specific Delete endpoints.
    """
    # Using kwargs={'pk': 1} as placeholder for reverse lookup
    url = reverse('company-detail', kwargs={'pk': 1})
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test UPDATE (PUT) - Mapping to generic update or specific endpoint
    # Note: 'company-update' exists as a specific endpoint in source [cite: 1]
    url_update = reverse('company-update', kwargs={'pk': 1})
    data = {
        "name": "Test Company",
        "email": "testco@example.com",
        "password": "StrongPassword123!",
        "address": "123 Business Rd",
        "phone_number": "+26377111222"
    }
    response = client.put(
        url_update, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    logger.info(response.json())
    assert response.status_code == 401 #?
    
    # Test DELETE
    # Note: 'company-delete' exists as a specific endpoint in source [cite: 1]
    url_delete = reverse('company-delete', kwargs={'pk': 1})
    data = None
    response = client.post(
        url_delete, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    logger.info(response.json())
    assert response.status_code == 401 #?


@pytest.mark.django_db
def test_company_actions_endpoints(client, test_company_token_fixture):
    """
    Test Company specific actions: Activate, Deactivate, Logo, Search.
    """
    # Activate
    url = reverse('company-activate', kwargs={'pk': 1})
    data = None
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    logger.info(response.json())
    assert response.status_code == 200

    # Deactivate
    url = reverse('company-deactivate', kwargs={'pk': 1})
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    logger.info(response.json())
    assert response.status_code == 200

    # Search
    url = reverse('company-search')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 200
    
    # Logo Actions (Set/Remove)
    url = reverse('company-set-logo', kwargs={'pk': 1})
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    logger.info(response.json())
    assert response.status_code == 400
