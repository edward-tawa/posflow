from fixture_tests import *

@pytest.mark.django_db
def test_branch_urls(client, test_company_token_fixture):
    """
    Test Branch endpoints.
    """
    url = reverse('branch-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    assert response.status_code == 200

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
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    assert response.status_code == 201

##########################################################################################################
###################################################################################################################

# ==========================================
# BRANCHES
# ==========================================

@pytest.mark.django_db
def test_branch_endpoints(client, test_company_token_fixture):
    """
    Test Branch List and Detail endpoints.
    """
    url = reverse('branch-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    assert response.status_code == 200

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
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    logger.info(response.json())
    assert response.status_code == 201
    
    # Test Detail (GET/UPDATE/DELETE)
    url_detail = reverse('branch-detail', kwargs={'pk': 1})
    
    # GET Detail
    response = client.get(url_detail, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
    logger.info(response.json())
    assert response.status_code == 404 #?

    # UPDATE
    response = client.put(
        url_detail, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    logger.info(response.json())
    assert response.status_code == 404 #?

    # DELETE
    response = client.delete(
        url_detail, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
    )
    logger.info(response.json())
    assert response.status_code == 404 #?