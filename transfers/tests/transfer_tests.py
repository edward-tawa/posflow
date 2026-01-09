# from fixture_tests import *

# @pytest.mark.django_db
# def test_cash_transfer_urls(client, test_company_token_fixture, test_company_get_fixture, create_branch_fixture, test_account_one_fixture, test_transfer_fixture, test_branch_account_fixture):
#     """
#     Test Cash Transfer endpoints.
#     """
#     url = reverse('cash-transfer-list')
#     logger.info(test_company_get_fixture)
#     # Test GET
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     logger.info(response.json())
#     assert response.status_code == 200

#     # Test CREATE
#     data = {
#         "company": test_company_get_fixture['id'],
#         "branch": create_branch_fixture['two'].id,
#         "source_account": test_account_one_fixture.get('acc1').id,
#         "destination_account": test_account_one_fixture.get('acc2').id,
#         "amount": "1000.00",
#         'transfer': test_transfer_fixture.id,
#         'source_branch': create_branch_fixture['two'].id,
#         'source_branch_id': create_branch_fixture['two'].id, 
#         'source_branch_account': test_branch_account_fixture.get('branch_account_one').id, 
#         'source_branch_account_id': test_branch_account_fixture.get('branch_account_one').id, 
#         'destination_branch': create_branch_fixture['one'].id, 
#         'destination_branch_id': create_branch_fixture['one'].id, 
#         'destination_branch_account': test_branch_account_fixture.get('branch_account_two').id, 
#         'destination_branch_account_id': test_branch_account_fixture.get('branch_account_two').id
#     }

#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 201

# @pytest.mark.django_db
# def test_product_transfer_urls(client, test_company_token_fixture, create_branch, test_transfer_fixture, test_product_fixture):
#     """
#     Test Product Transfer endpoints.
#     """
#     url = reverse('product-transfer-list')
    
#     # Test GET
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     logger.info(response.json())
#     assert response.status_code == 200

#     # Test CREATE
#     data = {
#         "transfer": test_transfer_fixture.id,
#         "source_branch": create_branch.id,
#         "destination_branch": create_branch.id,
#         "product": test_product_fixture.id
#     }
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 201

# @pytest.mark.django_db
# def test_product_transfer_item_urls(client, test_company_token_fixture):
#     """
#     Test Product Transfer Item endpoints.
#     """
#     url = reverse('product-transfer-item-list')
    
#     # Test GET
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     logger.info(response.json())
#     assert response.status_code == 200

#     # Test CREATE
#     data = {
#         "transfer": 1,
#         "product": 1,
#         "quantity": 10
#     }
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 403 #will comeback

# @pytest.mark.django_db
# def test_transfer_item_actions(client, test_company_token_fixture):
#     """
#     Test Product Transfer Item & Generic Transfer actions.
#     """
#     item_pk = 1
#     transfer_pk = 1

#     # 1. Product Transfer Item Actions
#     response = client.post(reverse('product-transfer-item-attach-to-product-transfer', args=[item_pk]), {"transfer_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 201
#     response = client.post(reverse('product-transfer-item-detach', args=[item_pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 201

#     # 2. Generic Transfer Update
#     response = client.post(reverse('transfer-update-status', args=[transfer_pk]), {"status": "COMPLETED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 201

# @pytest.mark.django_db
# def test_stock_transfer_workflow_actions(client, test_company_token_fixture):
#     """
#     Test Stock Transfer (Product Transfer) workflow actions.
#     """
#     pk = 1
#     # 1. Attach/Detach
#     response = client.post(reverse('product-transfer-attach-to-transfer', args=[pk]), {"item_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 201
#     response = client.post(reverse('product-transfer-detach', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 201

#     # 2. Execute Transfer
#     response = client.post(reverse('product-transfer-transfer', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 201

# @pytest.mark.django_db
# def test_cash_transfer_workflow_actions(client, test_company_token_fixture):
#     """
#     Test Cash Transfer workflow actions.
#     """
#     pk = 1
#     # 1. Hold/Release/Detach
#     response = client.post(reverse('cash-transfer-hold', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 201
    
#     response = client.post(reverse('cash-transfer-release', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 201
    
#     response = client.post(reverse('cash-transfer-detach', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 201

# @pytest.mark.django_db
# def test_generic_transfer_urls(client, test_company_token_fixture):
#     """
#     Test Generic Transfer endpoints.
#     (Distinct from CashTransfer and ProductTransfer)
#     """
#     url = reverse('transfer-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     assert response.status_code == 200

#     # Payload depends on what 'Transfer' represents in your system if different from others
#     # Assuming it might be a base class or a specific mixed transfer
#     data = {
#         "source_branch": 1,
#         "destination_branch": 2,
#         "transfer_type": "GENERAL",
#         "status": "PENDING"
#     }
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
#     )
#     assert response.status_code == 403 #will comeback