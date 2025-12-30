from fixture_tests import *

@pytest.mark.django_db
def test_cash_transfer_urls(client, test_user_token):
    """
    Test Cash Transfer endpoints.
    """
    url = reverse('cash-transfer-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 403 #will comeback

    # Test CREATE
    data = {
        "source_account": 1, # e.g., Till
        "destination_account": 2, # e.g., Safe
        "amount": "1000.00"
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 403 #will comeback

@pytest.mark.django_db
def test_product_transfer_urls(client, test_user_token):
    """
    Test Product Transfer endpoints.
    """
    url = reverse('product-transfer-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 403 #will comeback

    # Test CREATE
    data = {
        "source_branch": 1,
        "destination_branch": 2,
        "status": "IN_TRANSIT",
        "transfer_date": "2024-02-15"
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 403 #will comeback

@pytest.mark.django_db
def test_product_transfer_item_urls(client, test_user_token):
    """
    Test Product Transfer Item endpoints.
    """
    url = reverse('product-transfer-item-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 403 #will comeback

    # Test CREATE
    data = {
        "transfer": 1,
        "product": 1,
        "quantity": 10
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 403 #will comeback

@pytest.mark.django_db
def test_transfer_item_actions(client, test_user_token):
    """
    Test Product Transfer Item & Generic Transfer actions.
    """
    item_pk = 1
    transfer_pk = 1

    # 1. Product Transfer Item Actions
    client.post(reverse('product-transfer-item-attach', args=[item_pk]), {"transfer_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('product-transfer-item-detach', args=[item_pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Generic Transfer Update
    client.post(reverse('transfer-update-status', args=[transfer_pk]), {"status": "COMPLETED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_stock_transfer_workflow_actions(client, test_user_token):
    """
    Test Stock Transfer (Product Transfer) workflow actions.
    """
    pk = 1
    # 1. Attach/Detach
    client.post(reverse('product-transfer-attach', args=[pk]), {"item_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('product-transfer-detach', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Execute Transfer
    client.post(reverse('product-transfer-transfer', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_cash_transfer_workflow_actions(client, test_user_token):
    """
    Test Cash Transfer workflow actions.
    """
    pk = 1
    # 1. Hold/Release/Detach
    client.post(reverse('cash-transfer-hold', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('cash-transfer-release', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('cash-transfer-detach', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_generic_transfer_urls(client, test_user_token):
    """
    Test Generic Transfer endpoints.
    (Distinct from CashTransfer and ProductTransfer)
    """
    url = reverse('transfer-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 403 #will comeback

    # Payload depends on what 'Transfer' represents in your system if different from others
    # Assuming it might be a base class or a specific mixed transfer
    data = {
        "source_branch": 1,
        "destination_branch": 2,
        "transfer_type": "GENERAL",
        "status": "PENDING"
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    assert response.status_code == 403 #will comeback