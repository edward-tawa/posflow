from dotenv import load_dotenv
from loguru import logger
import pytest
import requests
import os

# load_dotenv()

# email = os.getenv('USER_EMAIL')
# password = os.getenv('USER_PASSWORD')

# @pytest.fixture
# def test_login():
#     login_url = 'http://127.0.0.1:8000/posflow/user/login/'
#     payload = {
#         'email': email,
#         'password': password
#     }
#     request_access_token = requests.post(url=login_url, data=payload)
#     logger.info(request_access_token.json().get('access_token'))
#     return request_access_token.json().get('access_token')

# def test_account_post(test_login):
#     account_post_url = 'http://127.0.0.1:8000/posflow/accounts/'
#     payload = {
#         'name': 'EMPLOYEE ACCOUNT',
#         'account_type': 'EMPLOYEE'
#     }
#     post_request = requests.post(url=account_post_url, data=payload, headers= {'Authorization': f'Bearer {test_login}'})
#     logger.info(post_request.json())
#     assert post_request.status_code == 201