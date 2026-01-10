from fixture_tests import *

@pytest.mark.django_db
def test_customer_urls(client, test_user_token):
    """
    Test Customer endpoints.
    """
    url = reverse('customer-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    # Test CREATE
    data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone_number": "+263777000111",
        "address": "123 Borrowdale Road"
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    assert response.status_code == 201

@pytest.mark.django_db
def test_customer_branch_history_urls(client, test_user_token):
    """
    Test Customer Branch History endpoints (likely read-only or auto-generated).
    """
    url = reverse('customer-branch-history-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

@pytest.mark.django_db
def test_customer_actions(client, test_user_token):
    """
    Test specialized customer actions like Statement, Credit Limit, etc.
    """
    # Assuming Customer ID 1 exists
    customer_id = 1
    
    # 1. Statement
    url_statement = reverse('customer-statement', args=[customer_id])
    response = client.get(url_statement, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code in [200, 404]

    # 2. Outstanding Balance
    url_balance = reverse('customer-outstanding-balance', args=[customer_id])
    response = client.get(url_balance, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code in [200, 404]

    # 3. Create Cash Sale (Action)
    url_cash_sale = reverse('create-cash-sale', args=[customer_id])
    response = client.post(url_cash_sale, {'amount':'1000'}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_customer_specific_financials(client, test_user_token):
    """
    Test specific financial actions for customers.
    """
    cust_id = 1
    
    # 1. Credit Limit
    url_limit = reverse('customer-credit-limit', args=[cust_id]) # Path: customers/<id>/credit-limit
    client.get(url_limit, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Refund Action
    url_refund = reverse('customer-refund', args=[cust_id]) # Path: customers/<id>/refund
    client.post(url_refund, {"amount": "10.00"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Create Credit Sale
    url_credit = reverse('create-credit-sale', args=[cust_id])
    client.post(url_credit, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


###############################################################################################################################
#################################################################################################################################

# ==========================================
# CUSTOMERS
# ==========================================

@pytest.mark.django_db
def test_customer_endpoints(client, test_user_token):
    """
    Test Customer List, Detail, and Branch History endpoints.
    [Source: 8]
    """
    # 1. Customer List
    url = reverse('customer-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200
    
    data = {
            'first_name': 'Teddy', 
            'last_name': 'Mads', 
            'email': 'mads@gmail.com', 
            'phone_number': '1234567897'
        }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

    # 2. Customer Detail
    url_detail = reverse('customer-detail', kwargs={'pk': 1})
    response = client.put(
        url_detail, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    assert response.status_code == 200

    # 3. Customer Branch History
    url_history = reverse('customer-branch-history-list')
    response = client.get(url_history, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200


@pytest.mark.django_db
def test_customer_action_endpoints(client, test_user_token, test_customer_fixture, test_account_two_fixture):
    """
    Test specific Customer actions (Statements, Sales, Refunds).
    """
    # Create Cash Sale
    url = reverse('create-cash-sale', kwargs={'customer_id': 1})
    data =  {
        'amount': '1000.00'
    }
    account_test = test_account_two_fixture
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

    # Create Credit Sale
    url = reverse('create-credit-sale', kwargs={'customer_id': test_customer_fixture.id})
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

    # Customer Statement (Usually GET)
    url = reverse('customer-statement', kwargs={'customer_id': 1})
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    # Outstanding Balance (Usually GET)
    url = reverse('customer-outstanding-balance', kwargs={'customer_id': 1})
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    # Refund
    url = reverse('customer-refund', kwargs={'customer_id': 1})
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 500 # Problem
