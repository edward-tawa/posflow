from accounts.models import *
from activity_log.models import *
from branch.models import *
from company.models import *
from config.models import *
from customers import *
from inventory.models import *
from loans.models import *
from notifications.models import *
from payments.models import *
from promotions.models import *
from reports.models import *
from sales.models import *
from suppliers.models import *
from taxes.models import *
from transactions.models import *
from transfers.models import *
from users.models import *

import pytest
from django.urls import reverse
from loguru import logger


#COMPANY
@pytest.fixture()
def test_company_fixture():
    company = Company.objects.create(
        name = 'Happy Go Lucky',
        email = 'happy@gmail.com',
        address = '27 Speke',
        phone_number = '+263785690'
    )
    return company

# Branch
@pytest.fixture
def create_branch(company):
    
    return Branch.objects.create(
        name = "Harare Main",
        company = company,
        code = "HRE-001",
        address = "123 Samora Machel Ave",
        city = "Harare",
        country = "Zimbabwe",
        phone_number = "+263777000000",
        is_active = True,
        manager = None
    )

from django.contrib.auth import get_user_model

@pytest.fixture
def create_user(db,test_company_fixture):
    User = get_user_model()
    user = User.objects.create_user(
        username = "testuser",
        first_name = "Teddy",
        last_name = "Chinomona",
        email = "test@example.com",
        password = 'teddy',
        company = test_company_fixture,
        role = "Manager",
        is_active = True,
        is_staff = False
    )
    return user


@pytest.fixture
def test_user_token(client, create_user):
    logger.info(
        {
            'email': create_user
        }
    )
    url = reverse('user-login')
    data = {
        'email': create_user.email,
        'password': 'teddy'
    }

    response = client.post(url, data, content_type='application/json')
    logger.info(response.json().get('access_token'))
    return response.json().get('access_token')


##########################################################################################################
@pytest.mark.django_db
def test_account_urls(client, test_user_token):
    logger.info(test_user_token)
    url = reverse('account-list')
    response = client.get(url)
    assert response.status_code == 200
    