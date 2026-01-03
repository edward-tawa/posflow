from fixture_tests import *

@pytest.mark.django_db
def test_fiscal_device_urls(client, test_user_token):
    """
    Test Fiscal Device endpoints.
    """
    url = reverse('fiscal-device-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "branch": 1,
        "device_name": "Epson T88V",
        "device_serial_number": "SN123456789",
        "device_type": "PRINTER", # Assuming Enum
        "is_active": True
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

@pytest.mark.django_db
def test_fiscal_document_urls(client, test_user_token, test_content_type_fixture, test_object_id_fixture):
    """
    Test Fiscal Document endpoints.
    """
    url = reverse('fiscal-document-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "fiscal_device": 1,
        "document_number": "DOC-001",
        "document_type": "Z_REPORT",
        "content_type": test_content_type_fixture.id,
        "object_id": test_object_id_fixture
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

@pytest.mark.django_db
def test_fiscal_invoice_urls(client, test_user_token, test_sale_fixture, test_object_id_fixture):
    """
    Test Fiscal Invoice endpoints.
    """
    url = reverse('fiscal-invoice-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "sale": test_sale_fixture.id,
        "invoice_number": test_object_id_fixture,
        "total_amount": 100,
        'total_tax': 10
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

@pytest.mark.django_db
def test_fiscal_invoice_item_urls(client, test_user_token, test_fiscal_invoice_fixture):
    """
    Test Fiscal Invoice Item endpoints.
    """
    url = reverse('fiscal-invoice-item-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "fiscal_invoice": test_fiscal_invoice_fixture.id,
        "description": "Item 1",
        "quantity": 1,
        "unit_price": 100.00,
        "tax_amount": 15.00,
        "tax_rate": 0.01
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

import json

@pytest.mark.django_db
def test_fiscal_response_urls(client, test_user_token, test_fiscal_invoice_fixture):
    """
    Test Fiscal Response endpoints (Logs from the device).
    """
    url = reverse('fiscal-response-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE (Usually created by system, but testing endpoint existence)
    data = {
        "fiscal_invoice": test_fiscal_invoice_fixture.id,
        "command": "PRINT_INVOICE",
        'response_code': 200, 
        'response_message': "{\"status\": \"OK\"}", 
        'raw_response': json.dumps({"status_code": 200, "message": "ok"})
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201
