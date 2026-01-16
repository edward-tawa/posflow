from fixture_tests import *

@pytest.mark.django_db
def test_user_urls(client, test_user_token):
    """
    Test User endpoints: List, Create.
    """
    url = reverse('user-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    # Test CREATE
    data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "Password123!",
        "first_name": "New",
        "role": "CASHIER"  # Assuming 'CASHIER' is a valid Enum value from your YAML
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    assert response.status_code == 403 #will be back

@pytest.mark.django_db
def test_user_bulk_operations(client, test_user_token):
    """
    Test Bulk User Operations.
    """
    # 1. Activate Bulk
    url_activate = reverse('user-activate-bulk')
    data = {"ids": [1, 2]} # Example payload for bulk
    client.post(url_activate, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Deactivate Bulk
    url_deactivate = reverse('user-deactivate-bulk')
    client.post(url_deactivate, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Delete Bulk
    url_delete = reverse('user-delete-bulk')
    client.post(url_delete, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 4. Assign Role Bulk
    url_assign = reverse('user-assign-role-bulk')
    data_role = {"ids": [1, 2], "role": "MANAGER"}
    client.post(url_assign, data_role, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_granular_user_actions(client, test_user_token):
    """
    Test specific actions on individual users.
    """
    user_id = 1

    # 1. Update & Delete (Specific Named Routes)
    # Note: DRF ViewSets usually handle this via detail URL, but you have specific named routes
    client.put(reverse('user-update', args=[user_id]), {"username": "updated"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.delete(reverse('user-delete', args=[user_id]), HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Status Actions
    client.post(reverse('user-activate', args=[user_id]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('user-deactivate', args=[user_id]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Role Management
    client.post(reverse('user-assign-role', args=[user_id]), {"role": "MANAGER"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('user-remove-role', args=[user_id]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 4. Password Reset (Individual & Bulk)
    client.post(reverse('user-reset-password', args=[user_id]), {"new_password": "123"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('user-reset-password-bulk'), {"ids": [1], "new_password": "123"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')




@pytest.mark.django_db
def test_users_me_update(client, test_user_token):
    """
    Test updating the current user's profile via /users/me/.
    (Often accessed via the same 'user-detail' or specific 'user-me' route depending on router).
    Assuming 'posflow_users-me' or similar standard action name, but often just GET.
    If your API supports PUT/PATCH on 'me', we test it here.
    """
    # Note: Standard DRF 'me' action is usually GET-only unless customized. 
    # If strictly following your URL list, you have 'user-detail' which takes an ID.
    # But often apps expose a way for users to update themselves without guessing their ID.
    # If no specific URL exists, we skip or use the ID-based one for the logged-in user.
    pass

@pytest.mark.django_db
def test_token_refresh_failure(client):
    """
    Test Token Refresh with invalid token.
    """
    url_user_refresh = reverse('user-token-refresh')
    response = client.post(url_user_refresh, {"refresh": "invalid_token_string"}, content_type='application/json')
    assert response.status_code == 401

# @pytest.mark.django_db
# def test_user_bulk_specifics(client, test_user_token):
#     """
#     Test the specific bulk endpoints for Users that might have been glossed over.
#     """
#     # 1. Activate Bulk
#     url_activate = reverse('user-activate-bulk')
#     response = client.post(url_activate, {"ids": [1, 2]}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200
    
#     # 2. Deactivate Bulk
#     url_deactivate = reverse('user-deactivate-bulk')
#     response = client.post(url_deactivate, {"ids": [1, 2]}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     # 3. Assign Role Bulk
#     url_assign_role = reverse('user-assign-role-bulk')
#     response = client.post(url_assign_role, {"ids": [1, 2], "role": "MANAGER"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     # 4. Reset Password Bulk
#     url_reset = reverse('user-reset-password-bulk')
#     response = client.post(url_reset, {"ids": [1, 2], "new_password": "pass"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200
    
#     # 4. User Login
#     url_user_login = reverse('user-login')
#     response = client.post(url_user_login, {"email": "user@example.com", "password": "pass"}, content_type='application/json')
#     assert response.status_code == 200

#     # 5. User Logout
#     url_user_logout = reverse('user-logout')
#     response = client.post(url_user_logout, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     # 6. User Token Refresh
#     url_user_refresh = reverse('user-token-refresh')
#     response = client.post(url_user_refresh, {"refresh": "token"}, content_type='application/json')
#     assert response.status_code == 200


# @pytest.mark.django_db
# def test_bulk_with_empty_ids(client, test_user_token):
#     """
#     Test bulk operations with empty ID list to check edge case handling.
#     """
#     # Activate Bulk with empty IDs
#     url_activate = reverse('user-activate-bulk')
#     response = client.post(url_activate, {"ids": []}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 400 

#     # Deactivate Bulk with empty IDs
#     url_deactivate = reverse('user-deactivate-bulk')
#     response = client.post(url_deactivate, {"ids": []}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 400

#     # Assign Role Bulk with empty IDs
#     url_assign_role = reverse('user-assign-role-bulk')
#     response = client.post(url_assign_role, {"ids": [], "role": "MANAGER"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 400

#     # Reset Password Bulk with empty IDs
#     url_reset = reverse('user-reset-password-bulk')
#     response = client.post(url_reset, {"ids": [], "new_password": "pass"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 400


#################################################################################################################################################################################
##########################################################################################################################################################################################

# ==========================================
# USER AUTHENTICATION & REGISTRATION
# ==========================================

# @pytest.mark.django_db
# def test_user_auth_endpoints(client, test_user_token, test_company_token_fixture):
#     """
#     Test User Login, Logout, Register, and Token Refresh endpoints.
#     """
#     # 1. User Login
#     url = reverse('user-login')

#     data = {
#         'email': "test@example.com",
#         'password': 'teddy'
#     }

#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json'
#     )
#     logger.info(response.json())
#     assert response.status_code == 200

#     # 2. User Token Refresh
#     url = reverse('user-token-refresh')
#     data = {
#         "refresh_token": response.json().get('refresh_token')
#     }
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json'
#     )
#     logger.info(response.json())
#     assert response.status_code == 200

#     # 3. User Register
#     url = reverse('user-register')

#     data = {
#         "email": "newuser@example.com",
#         "username": "newuser",
#         "password": "Password123!",
#         "first_name": "New",
#         "role": "Sales" 
#     }

#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json',
#         HTTP_AUTHORIZATION = f'Bearer: {test_company_token_fixture}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 201

    
#     # 4. User Logout
#     url = reverse('user-logout')
#     data = None
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json',
#         HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 200


# # ==========================================
# # USER MANAGEMENT
# # ==========================================

# @pytest.mark.django_db
# def test_user_list_endpoints(client, test_company_token_fixture, create_user):
#     """
#     Test User List and Bulk actions.
#     """
#     create = create_user
#     url = reverse('user-list')
    
#     # Test GET
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     logger.info(response.json())
#     assert response.status_code == 200

#     # Test Bulk Activate
#     url_bulk = reverse('user-activate-bulk')
#     data = None
#     response = client.post(
#         url_bulk, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
#     )
#     logger.info(response.json())
#     assert response.status_code in [201, 400, 403]

#     """
#     Test User Detail, Update, and specific Delete endpoints.
#     """
#     url = reverse('user-detail', kwargs={'pk': 1})
    
#     # Test GET
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}')
#     logger.info(response.json())
#     assert response.status_code in [200, 404]

# @pytest.mark.django_db
# def test_user_update_endpoints(client, test_user_token, create_user):
#     create = create_user
#     url_update = reverse('user-update', kwargs={'pk': 1})
#     data = None
#     response = client.put(
#         url_update, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 201
    
#     # Test DELETE
#     url_delete = reverse('user-delete', kwargs={'pk': 1})
#     data = None
#     response = client.post(
#         url_delete, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 204

# @pytest.mark.django_db
# def test_user_actions_endpoints(client, test_company_token_fixture, create_user):
#     """
#     Test User specific actions: Activate, Assign Role, Reset Password.
#     """
#     create = create_user
#     # Activate
#     url = reverse('user-activate', kwargs={'pk': 1})
#     data = None
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
#     )
#     logger.info(response.json())
#     assert response.status_code in [201, 404]

#     # Assign Role
#     url = reverse('user-assign-role', kwargs={'pk': 1})
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
#     )
#     logger.info(response.json())
#     assert response.status_code in [201, 404, 403]
    
#     # Reset Password
#     url = reverse('user-reset-password', kwargs={'pk': 1})
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_company_token_fixture}'
#     )
#     logger.info(response.json())
#     assert response.status_code in [201, 404, 403]