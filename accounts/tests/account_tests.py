from fixture_tests import *
import pytest


@pytest.mark.django_db
def test_account_urls(client, test_user_token):
    """
    Test Base Account endpoints.
    """
    url = reverse('account-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    # Test CREATE
    data = {
        "name": "General Ledger",
        "account_type": "BANK"
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
def test_branch_account_urls(client, test_user_token):
    """
    Test Branch Account endpoints.
    Dependencies: Account, Branch (IDs assumed to be 1 for test)
    """
    url = reverse('branch-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    # Create
    data = {
        "account": 1,
        "branch": 1
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    # Assuming standard DRF create behavior
    if response.status_code != 201:
        logger.warning(f"Branch Account Create failed: {response.data}")

@pytest.mark.django_db
def test_customer_account_urls(client, test_user_token):
    """
    Test Customer Account endpoints.
    Dependencies: Account, Customer
    """
    url = reverse('customer-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    data = {
        "account": 1,
        "customer": 1
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_employee_account_urls(client, test_user_token):
    """
    Test Employee Account endpoints.
    Dependencies: Account, Employee
    """
    url = reverse('employee-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    data = {
        "account": 1,
        "employee": 1
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_loan_account_urls(client, test_user_token):
    """
    Test Loan Account endpoints.
    Dependencies: Account, Loan
    """
    url = reverse('loan-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    data = {
        "account": 1,
        "loan": 1
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_supplier_account_urls(client, test_user_token):
    """
    Test Supplier Account endpoints.
    Dependencies: Account, Supplier
    """
    url = reverse('supplier-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    data = {
        "account": 1,
        "supplier": 1
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_bank_account_urls(client, test_user_token,test_account_fixture):
    """
    Test Bank Account endpoints.
    Dependencies: Account (OneToOne usually)
    """
    url = reverse('bank-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200 #will comeback
    logger.info(test_account_fixture.id)
    data = {
        "account": test_account_fixture.id,
        "bank_name": "CABS"
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
def test_cash_account_urls(client, test_user_token, test_account_fixture):
    """
    Test Cash Account endpoints.
    Dependencies: Account (OneToOne usually)
    """
    url = reverse('cash-account-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    # Test CREATE
    data = {
        "account": test_account_fixture.id  # Required: ID of an existing Account
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    # 201 Created or 200 OK depending on implementation details
    assert response.status_code in [200, 201]

@pytest.mark.django_db
def test_sales_account_urls(client, test_user_token, test_account_fixture, create_user):
    """
    Test Sales Account endpoints.
    """
    url = reverse('sales-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    data = {
        "account": test_account_fixture.id,
        "sales_person": create_user.id # Optional usually, but testing full payload
    }
    response = client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 201

@pytest.mark.django_db
def test_purchases_account_urls(client, test_user_token):
    """
    Test Purchases Account endpoints.
    """
    url = reverse('purchases-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    data = {
        "account": 1,
        "supplier": 1 # Optional link to supplier
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_expense_account_urls(client, test_user_token):
    """
    Test Expense Account endpoints.
    """
    url = reverse('expense-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    data = {
        "account": 1,
        "description": "Office Supplies"
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_supplier_account_detail(client, test_user_token):
    """
    Explicitly test Supplier Account detail retrieval.
    URL Name: 'supplier-account-detail'
    """
    pk = 1
    url = reverse('supplier-account-detail', args=[pk])
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    # 200 if exists, 404 if not found (standard DRF behavior)
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_customer_account_detail(client, test_user_token):
    """
    Explicitly test Customer Account detail retrieval.
    URL Name: 'customer-account-detail'
    """
    pk = 1
    url = reverse('customer-account-detail', args=[pk])
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_employee_account_detail(client, test_user_token):
    """
    Explicitly test Employee Account detail retrieval.
    URL Name: 'employee-account-detail'
    """
    pk = 1
    url = reverse('employee-account-detail', args=[pk])
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_loan_account_detail(client, test_user_token):
    """
    Explicitly test Loan Account detail retrieval.
    URL Name: 'loan-account-detail'
    """
    pk = 1
    url = reverse('loan-account-detail', args=[pk])
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_cash_account_detail(client, test_user_token):
    """
    Explicitly test Cash Account detail retrieval.
    URL Name: 'cash-account-detail'
    """
    pk = 1
    url = reverse('cash-account-detail', args=[pk])
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_sales_account_detail(client, test_user_token):
    """
    Explicitly test Sales Account detail retrieval.
    URL Name: 'sales-account-detail'
    """
    pk = 1
    url = reverse('sales-account-detail', args=[pk])
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_purchases_account_detail(client, test_user_token):
    """
    Explicitly test Purchases Account detail retrieval.
    URL Name: 'purchases-account-detail'
    """
    pk = 1
    url = reverse('purchases-account-detail', args=[pk])
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_expense_account_detail(client, test_user_token):
    """
    Explicitly test Expense Account detail retrieval.
    URL Name: 'expense-account-detail'
    """
    pk = 1
    url = reverse('expense-account-detail', args=[pk])
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code in [200, 404]

@pytest.mark.django_db
def test_sales_returns_account_urls(client, test_user_token):
    """
    Test Sales Returns Account endpoints.
    """
    url = reverse('sales-returns-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    data = {
        "account": 1,
        "description": "Sales Returns Ledger"
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_purchases_returns_account_urls(client, test_user_token):
    """
    Test Purchases Returns Account endpoints.
    """
    url = reverse('purchases-returns-account-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    data = {
        "account": 1,
        "description": "Purchase Returns Ledger"
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


#############################################################################################
#######################################################################################################

# ==========================================
# ENTITY ACCOUNTS (Branch, Customer, Employee, Supplier, Loan)
# ==========================================

@pytest.mark.django_db
def test_entity_account_endpoints(client, test_user_token, test_account_fixture, test_customer_fixture, create_loan_fixture, test_supplier_fixture):
    """
    Test Branch, Customer, Employee, Loan, and Supplier Account endpoints.
    [Source: 5, 6]
    """
    # Define the list of entity account url names
    account_types = [
        'branch-account-list',
        'customer-account-list',
        'employee-account-list',
        'loan-account-list',
        'supplier-account-list'
    ]

    for route_name in account_types:
        url = reverse(route_name)
        
        # Test GET
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
        assert response.status_code == 200

        # Test CREATE
        data = {
            "account": test_account_fixture.id,
            "customer": test_customer_fixture.id,
            "employee": 1,
            "loan": create_loan_fixture.id,
            "supplier": test_supplier_fixture.id

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
def test_entity_account_details(client, test_user_token, test_account_fixture, test_customer_fixture, create_loan_fixture, test_supplier_fixture, create_entity_account_fixture):
    """
    Test Detail endpoints for Entity Accounts.
    [Source: 5, 6]
    """
    detail_types = [
        'branch-account-detail',
        'customer-account-detail',
        'employee-account-detail',
        'loan-account-detail',
        'supplier-account-detail'
    ]

    for route_name in detail_types:
        create_entries  = create_entity_account_fixture
        url = reverse(route_name, kwargs={'pk': 1})
        
        # Test GET
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
        logger.info([response.json(), response.status_code])
        assert response.status_code in [200, 404]

        # Test UPDATE
        data = {
            "account": test_account_fixture.id,
            "customer": test_customer_fixture.id,
            "employee": 1,
            "loan": create_loan_fixture.id,
            "supplier": test_supplier_fixture.id
        }
        response = client.put(
            url, 
            data, 
            content_type='application/json', 
            HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
        )
        logger.info(response.json())
        assert response.status_code in [201, 200]


# ==========================================
# FINANCIAL ACCOUNTS (General, Bank, Cash)
# ==========================================

@pytest.mark.django_db
def test_financial_account_endpoints(client, test_user_token, test_account_fixture):
    """
    Test General, Bank, and Cash Account endpoints.
    [Source: 6]
    """
    account_types = [
        'account-list',
        'bank-account-list',
        'cash-account-list'
    ]

    for route_name in account_types:
        url = reverse(route_name)
        
        # Test GET
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
        assert response.status_code == 200

        # Test CREATE
        data = {
            "name": "Test Acc",
            "account_type": "BRANCH",
            "account": test_account_fixture.id,
            "branch": 1,
            "bank_name": "BancABC"
        }
        response = client.post(
            url, 
            data, 
            content_type='application/json', 
            HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
        )
        logger.info(response.json())
        assert response.status_code == 201

         
    url_detail = reverse('account-detail', kwargs={'pk': 1})
    data = {
        "name": "Test Acc 2",
        "account_type": "CUSTOMER"
    }
    response = client.put(
        url_detail, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 200


# ==========================================
# TRADING ACCOUNTS (Sales, Purchases, Returns, Expenses)
# ==========================================

@pytest.mark.django_db
def test_trading_account_endpoints(client, test_user_token, test_account_fixture, test_expense_fixture):
    """
    Test Sales, Purchases, Returns, and Expense Account endpoints.
    """
    trading_types = [
        'sales-account-list',
        'purchases-account-list',
        'sales-returns-account-list',
        'purchases-returns-account-list',
        'expense-account-list'
    ]

    for route_name in trading_types:
        url = reverse(route_name)
        
        # Test GET
        response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
        assert response.status_code == 200

        # Test CREATE
        data = {
            "account": test_account_fixture.id,
            "expense": test_expense_fixture.id
        }
        response = client.post(
            url, 
            data, 
            content_type='application/json', 
            HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
        )
        logger.info(response.json())
        assert response.status_code == 201