from fixture_tests import *

# ==========================================
# LOANS
# ==========================================

@pytest.mark.django_db
def test_loan_endpoints(client, test_user_token):
    """
    Test Loan List and Detail endpoints.
    """
    url = reverse('loan-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200
    
    # Test CREATE
    data = {
        "borrower": 1, 
        "loan_amount": 1000.00,
        "interest_rate": 0.05,
        "start_date": date.today(),
        "end_date": date.today() + timedelta(days=10),
        "issued_by": 1,
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

    # Test Detail
    url_detail = reverse('loan-detail', kwargs={'pk': 1})
    response = client.get(url_detail, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200
    
    # Test UPDATE
    response = client.put(
        url_detail, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    assert response.status_code == 200
