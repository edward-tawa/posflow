from fixture_tests import *

@pytest.mark.django_db
def test_loan_urls(client, test_user_token, create_user):
    """
    Test Loan endpoints.
    """
    url = reverse('loan-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "borrower": create_user.id,
        "loan_amount": "500.00",
        "interest_rate": "5.00",
        'start_date': "2025-12-31", #Logic error
        "end_date": "2024-12-31"
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201