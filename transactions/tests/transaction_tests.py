from fixture_tests import *

@pytest.mark.django_db
def test_transaction_urls(client, test_user_token, test_dc_fixture):
    """
    Test Transaction endpoints (General Ledger entries).
    """
    url = reverse('transaction-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "account": 1,
        "amount": "500.00",
        "transaction_type": "INCOMING",
        "description": "Manual Adjustment",
        'debit_account': test_dc_fixture.get('debit').id, 
        'credit_account': test_dc_fixture.get('credit').id, 
        'transaction_category': 'CASH SALE'
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
def test_transaction_item_urls(client, test_user_token, test_product_fixture, test_transaction_fixture):
    """
    Test Transaction Item endpoints (Splits).
    """
    url = reverse('transactionitem-list') # Note: 'transactionitem-list' per provided urls
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200
    
    # Test CREATE
    data = {
        "transaction": test_transaction_fixture.id,
        "amount": "250.00",
        "description": "Split 1",
        'product': test_product_fixture.id, 
        'quantity': 5, 
        'unit_price': 2.70, 
        'tax_rate': 0.02
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

######################################################################################################
##############################################################################################################

# ==========================================
# TRANSACTIONS
# ==========================================

# @pytest.mark.django_db
# def test_transaction_endpoints(client, test_user_token):
#     """
#     Test Transaction List and Detail.
#     [Source: 34]
#     """
#     url = reverse('transaction-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     data = None
#     response = client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 201

#     # Detail
#     url_detail = reverse('transaction-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


@pytest.mark.django_db
def test_transaction_item_endpoints(client, test_user_token):
    """
    Test Transaction Item List and Detail.
    [Source: 34]
    """
    url = reverse('transactionitem-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    # Detail
    url_detail = reverse('transactionitem-detail', kwargs={'pk': 1})
    client.get(url_detail, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')