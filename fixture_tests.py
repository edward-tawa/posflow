from accounts.models import *
from activity_log.models import *
from branch.models import *
from company.models import *
from config.models import *
from customers.models import *
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
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from datetime import date
import pytest
from django.urls import reverse
from loguru import logger

#===========================================
#COMPANY Fixture
#===========================================
@pytest.fixture()
def test_company_fixture():
    company = Company.objects.create(
        name = 'Happy Go Lucky',
        email = 'happy@gmail.com',
        address = '27 Speke',
        phone_number = '+263785690'
    )
    return company


#=========================================
# Branch Fixture
#=========================================
@pytest.fixture
def create_branch(test_company_fixture):
    """
    Creates and returns a Branch instance for testing.
    """
    return Branch.objects.create(
        name = "Harare Main",
        company = test_company_fixture,
        code = "HRE-001",
        address = "123 Samora Machel Ave",
        city = "Harare",
        country = "Zimbabwe",
        phone_number = "+263777000000",
        is_active = True,
        manager = None
    )


#=========================================
# User Fixture
#=========================================
@pytest.fixture
def create_user(db,test_company_fixture, create_branch):
    """
    Creates and returns a User instance for testing.
    """
    User = get_user_model()
    user = User.objects.create_user(
        username = "testuser",
        first_name = "Teddy",
        last_name = "Chinomona",
        email = "test@example.com",
        password = 'teddy',
        company = test_company_fixture,
        branch = create_branch,
        role = "Manager",
        is_active = True,
        is_staff = False
    )
    return user


#=========================================
# Login Fixture
#=========================================
@pytest.fixture
def test_user_token(client, create_user):
    """
    Creates and returns a user token for testing.
    """
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


#=========================================
# Account fixture
#=========================================
@pytest.fixture()
def test_account_fixture(test_company_fixture, create_branch):
    """
    Creates and returns an Account instance for testing.
    """
    # CREATE
    account = Account.objects.create(
        name = 'Test Account',
        company = test_company_fixture,
        branch = create_branch,
        account_number = Account.generate_account_number(self='account'),
        account_type = 'CASH',
    )
    return account

#=========================================
# Account 1 fixture
#=========================================
@pytest.fixture()
def test_account_one_fixture(test_company_fixture, create_branch):
    """
    Creates and returns two Account instances for testing.
    """
    # CREATE
    account_one = Account.objects.create(
        name = 'Test 1 Account',
        company = test_company_fixture,
        branch = create_branch,
        account_number = Account.generate_account_number(self='account'),
        account_type = 'BANK',
    )
    account_two = Account.objects.create(
        name = 'Test Account',
        company = test_company_fixture,
        branch = create_branch,
        account_number = Account.generate_account_number(self='account'),
        account_type = 'CASH',
    )
    return {
        "acc1": account_one,
        "acc2": account_two
    }

#=========================================
# Account 2 fixture
#=========================================
@pytest.fixture()
def test_account_two_fixture(test_company_fixture, create_branch):
    """
    Creates and returns two Account instances for testing.
    """
    # CREATE
    account_one = Account.objects.create(
        name = 'Test 1 Account',
        company = test_company_fixture,
        branch = create_branch,
        account_number = Account.generate_account_number(self='account'),
        account_type = 'CUSTOMER',
    )
    account_two = Account.objects.create(
        name = 'Test Account',
        company = test_company_fixture,
        branch = create_branch,
        account_number = Account.generate_account_number(self='account'),
        account_type = 'SALE',
    )
    account_three = Account.objects.create(
        name = 'Test Account 3',
        company = test_company_fixture,
        branch = create_branch,
        account_number = Account.generate_account_number(self='account'),
        account_type = 'CASH',
    )

    cash = CashAccount.objects.create(
        account = account_three,
        branch = create_branch
    )
    return {
        "acc1": account_one,
        "acc2": account_two,
        "acc3": account_three,
        "cash": cash
    }

#=========================================
# Debit&Credit Account fixture
#=========================================
@pytest.fixture()
def test_dc_fixture(test_company_fixture, create_branch):
    """
    Creates and returns debit and credit Account instances for testing.
    """
    # CREATE
    debit_account = Account.objects.create(
        name = 'Test Debit Account',
        company = test_company_fixture,
        branch = create_branch,
        account_number = Account.generate_account_number(self='account'),
        account_type = 'CASH',
    )

    credit_account = Account.objects.create(
        name = 'Test Credit Account',
        company = test_company_fixture,
        branch = create_branch,
        account_number = Account.generate_account_number(self='account'),
        account_type = 'CUSTOMER',
    )
    return {
        "debit": debit_account,
        "credit": credit_account
    }


#=========================================
# Product Category Fixture
#=========================================
@pytest.fixture()
def test_product_category_fixture(create_branch, test_company_fixture):
    """
    Creates and returns a ProductCategory instance for testing.
    """
    return ProductCategory.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        name = 'Test Category',
        description = 'Testing category dependencies'
    )


#=========================================
# Product Fixture
#=========================================
@pytest.fixture()
def test_product_fixture(create_branch, test_company_fixture, test_product_category_fixture):
    """
    Creates and returns a Product instance for testing.
    """
    product = Product(
        company = test_company_fixture,
        branch = create_branch,
        name = 'HP Omen',
        description = 'HIGH PERFOMANCE PC',
        price = 1560,
        product_category = test_product_category_fixture,
        stock = 25
    )

    product.sku = Product.generate_sku(product)
    product.save()
    return product


#=========================================
# Stocktake Fixture
#=========================================
@pytest.fixture()
def test_stocktake_fixture(create_branch, test_company_fixture, create_user):
    """
    Creates and returns a StockTake instance for testing.
    """
    return StockTake.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        quantity_counted = 100,
        performed_by = create_user,
        status = 'pending',
        reference_number = StockTake.generate_reference_number(),
        notes = 'First test stoaktake'
    )


#=========================================
# Payment Fixture
#=========================================
@pytest.fixture()
def test_payment_fixture(create_branch, test_company_fixture, create_user):
    """
    Creates and returns a Payment instance for testing.
    """
    return Payment.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        paid_by = create_user,
        payment_type = 'incoming',
        payment_number = Payment.generate_payment_number(self=Payment),
        amount = 10000.00,
        status = 'pending',
        method = 'swipe',
    )


#=========================================
# Customer Fixture
#=========================================
@pytest.fixture()
def test_customer_fixture(create_branch, test_company_fixture):
    """
    Creates and returns a Customer instance for testing.
    """
    return Customer.objects.create(
        first_name = 'Magiv',
        last_name = 'Kasikna',
        email = 'mkasikna@gmail.com',
        phone_number = '+263784672',
        company = test_company_fixture,
        branch = create_branch,
        address = 'Kaguvi 63',
        notes = 'Lady'
    )


#=========================================
# SaleOrder Fixture
#=========================================
@pytest.fixture()
def test_sale_order_fixture(create_branch, test_company_fixture, create_user, test_customer_fixture):
    """
    Creates and returns a SalesOrder instance for testing.
    """
    return SalesOrder.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        customer = test_customer_fixture,
        order_number = SalesOrder.generate_unique_order_number(self=SalesOrder),
        customer_name = test_customer_fixture.first_name,
        total_amount = 10000.00,
        sales_person = create_user,
        notes = 'Test 1'
    )


#=========================================
# SaleReturn Fixture
#=========================================
@pytest.fixture()
def test_sale_return_fixture(create_branch, test_company_fixture, create_user, test_customer_fixture, test_sale_order_fixture):
    """
    Creates and returns a SalesReturn instance for testing.
    """
    return SalesReturn.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        customer = test_customer_fixture,
        sale_order = test_sale_order_fixture,
        return_number = SalesReturn.generate_return_number(SalesReturn),
        return_date = date.today(),
        total_amount = 100,
        processed_by = create_user,
    )

#=========================================
# SaleReceipt Fixture
#=========================================

@pytest.fixture()
def test_sale_receipt_fixture(create_branch, test_company_fixture, create_user, test_customer_fixture, test_sale_order_fixture):
    """
    Creates and returns a SalesReceipt instance for testing.
    """
    return SalesReceipt.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        customer = test_customer_fixture,
        sales_order = test_sale_order_fixture,
        receipt_number = SalesReceipt.generate_receipt_number(SalesReceipt),
        total_amount = 1000.00,
        issued_by = create_user,
    )


#=========================================
# SalePayment Fixture
#=========================================
@pytest.fixture()
def test_sale_payment_fixture(test_sale_order_fixture, test_sale_fixture, test_sale_receipt_fixture, test_payment_fixture):
    """
    Creates and returns a SalesPayment instance for testing.
    """
    return SalesPayment.objects.create(
        sales_order = test_sale_order_fixture,
        sale = test_sale_fixture,
        sales_receipt = test_sale_receipt_fixture,
        payment = test_payment_fixture,
        amount_applied = 100
    )


#=========================================
# Sale Fixture
#=========================================
@pytest.fixture()
def test_sale_fixture(create_branch, test_company_fixture, create_user, test_customer_fixture):
    """
    Creates and returns a Sale instance for testing.
    """
    return Sale.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        customer = test_customer_fixture,
        total_amount = 100,
        tax_amount = 0.05,
        sale_number = Sale.generate_sale_number(Sale),
        issued_by = create_user
    )


#=========================================
# SaleQuotation Fixture
#=========================================
@pytest.fixture()
def test_sale_quotation_fixture(create_branch, test_company_fixture, create_user, test_customer_fixture):
    """
    Creates and returns a SalesQuotation instance for testing.
    """
    return SalesQuotation.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        quotation_number = SalesQuotation.generate_quotation_number(SalesQuotation),
        customer = test_customer_fixture,
        valid_until = date.today(),
        total_amount = 1200,
        created_by = create_user,
    )


#=========================================
# DeliveryNote Fixture
#=========================================
@pytest.fixture()
def test_delivery_note_fixture(create_branch, test_company_fixture, create_user, test_customer_fixture, test_sale_order_fixture):
    """
    Creates and returns a DeliveryNote instance for testing.
    """
    return DeliveryNote.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        customer = test_customer_fixture,
        sales_order = test_sale_order_fixture,
        delivery_number = DeliveryNote.generate_delivery_number(DeliveryNote),
        total_amount = 1236,
        issued_by = create_user
    )


#=========================================
# Supplier Fixture
#=========================================
@pytest.fixture()
def test_supplier_fixture(create_branch, test_company_fixture):
    """
    Creates and returns a Supplier instance for testing.
    """
    return Supplier.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        name = 'WE SUPPLY',
        email = 'we@gmail.com',
        phone_number = '+2637834509',
        address = 'Harare'
    )


#=========================================
# PurchaseOrder Fixture
#=========================================
@pytest.fixture()
def test_purchase_order_fixture(test_company_fixture, test_supplier_fixture):
    """
    Creates and returns a PurchaseOrder instance for testing.
    """
    return PurchaseOrder.objects.create(
        company = test_company_fixture,
        supplier = test_supplier_fixture,
        quantity_ordered = 100,
        total_amount = 20.50,
        status = "pending",
        reference_number = PurchaseOrder.generate_reference_number(PurchaseOrder),
    )


#=========================================
# SupplierDebitNote Fixture
#=========================================
@pytest.fixture()
def test_supplier_debit_note_fixture(test_company_fixture, test_supplier_fixture):
    """
    Creates and returns a SupplierDebitNote instance for testing.
    """
    return SupplierDebitNote.objects.create(
        company = test_company_fixture,
        supplier = test_supplier_fixture,
        debit_note_number = SupplierDebitNote.generate_debit_note_number(SupplierDebitNote),
        total_amount = 350.60
    )


#=========================================
# SupplierCreditNote Fixture
#=========================================
@pytest.fixture()
def test_supplier_credit_note_fixture(test_company_fixture, test_supplier_fixture):
    """
    Creates and returns a SupplierCreditNote instance for testing.
    """
    return SupplierCreditNote.objects.create(
        company = test_company_fixture,
        supplier = test_supplier_fixture,
        credit_note_number = SupplierCreditNote.generate_credit_note_number(SupplierCreditNote),
        total_amount = 350.60
    )


#=========================================
# PurchaseInvoice Fixture
#=========================================
@pytest.fixture()
def test_purchase_invoice_fixture(test_company_fixture, test_supplier_fixture, create_branch, test_purchase_order_fixture, test_purchase_fixture):
    """
    Creates and returns a PurchaseInvoice instance for testing.
    """
    return PurchaseInvoice.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        purchase = test_purchase_fixture,
        supplier = test_supplier_fixture,
        purchase_order = test_purchase_order_fixture,
        invoice_number = PurchaseInvoice.generate_invoice_number(PurchaseInvoice),
    )


#=========================================
# Purchase Fixture
#=========================================
@pytest.fixture()
def test_purchase_fixture(test_company_fixture, test_supplier_fixture, create_branch):
    """
    Creates and returns a Purchase instance for testing.
    """
    return Purchase.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        supplier = test_supplier_fixture,
        purchase_number = Purchase.generate_purchase_number(Purchase)
    )


#=========================================
# PurchaseReturn Fixture
#=========================================
@pytest.fixture()
def test_purchase_return_fixture(test_company_fixture, test_supplier_fixture, create_branch, test_purchase_order_fixture):
    """
    Creates and returns a PurchaseReturn instance for testing.
    """
    return PurchaseReturn.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        supplier = test_supplier_fixture,
        purchase_return_number = PurchaseReturn.generate_purchase_return_number(PurchaseReturn),
        purchase_order = test_purchase_order_fixture
    )


#=========================================
# PurchasePayment Fixture
#=========================================
@pytest.fixture()
def test_purchase_payment_fixture(test_supplier_fixture, test_purchase_invoice_fixture, test_payment_fixture):
    """
    Creates and returns a PurchasePayment instance for testing.
    """
    return PurchasePayment.objects.create(
        supplier = test_supplier_fixture,
        payment = test_payment_fixture,
        purchase_invoice = test_purchase_invoice_fixture,
        amount_paid = 100
    )


#=========================================
# ContentType Fixture
#=========================================
@pytest.fixture()
def test_content_type_fixture():
    """
    Creates and returns a ContentType instance for testing.
    """
    return ContentType.objects.create(
        app_label = "taxes",
        model = "FiscalDocument"
    )


#=========================================
# ObjectID Fixture
#=========================================
from uuid import uuid4
@pytest.fixture()
def test_object_id_fixture():
    """
    Creates and returns a UUID instance for testing.
    """
    return uuid4()


#=========================================
# FiscalInvoice Fixture
#=========================================
@pytest.fixture()
def test_fiscal_invoice_fixture(test_company_fixture, create_branch, test_sale_fixture, test_object_id_fixture):
    """
    Creates and returns a FiscalInvoice instance for testing.
    """
    return FiscalInvoice.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        sale = test_sale_fixture,
        invoice_number = test_object_id_fixture,
        total_amount = 1000,
        total_tax = 10
    )


#=========================================
# Transaction Fixture
#=========================================
@pytest.fixture()
def test_transaction_fixture(test_company_fixture, create_branch, test_dc_fixture, test_customer_fixture):
    """
    Creates and returns a Transaction instance for testing.
    """
    return Transaction.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        customer = test_customer_fixture,
        debit_account = test_dc_fixture.get('debit'),
        credit_account = test_dc_fixture.get('credit'),
        transaction_type = 'INCOMING',
        transaction_category = 'CASH SALE',
        total_amount = 1000.00,
        transaction_number = Transaction.generate_transaction_number(Transaction)
    )

@pytest.fixture()
def test_write_off_account_fixture():
    """
    Creates and returns a WriteOffAccount instance for testing.
    """
    pass


#=============================================
# Company Login Fixture
#=============================================

@pytest.fixture()
def test_company_token_fixture(client):
    """
    Creates and returns a company token for testing.
    """
    url = reverse('company-register')
    data = {
        "name": "TechCity",
        "email": "techcity@gmail.com",
        "password": "techcity",
        "address": "63 Speke",
        "phone_number": "078467231"
    }

    response = client.post(url, data)
    logger.info(response.status_code)

    if response.status_code == 201:
        url = reverse('company-login')
        data = {
            'email': "techcity@gmail.com",
            "password": "techcity"
        }
        response = client.post(url, data)
        logger.info(response.json())

        return response.json().get('access_token')
    
#==============================================
# Transfer Fixture
#==============================================
@pytest.fixture()
def test_transfer_fixture(test_company_fixture, create_branch):
    """
    Creates and returns a Transfer instance for testing.
    """
    return Transfer.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        reference_number = Transfer.generate_reference_number(Transfer)
    )

#==============================================
# Branch Account
#==============================================
@pytest.fixture()
def test_branch_account_fixture(test_company_fixture, create_branch, test_account_one_fixture):
    """
    Creates and returns BranchAccount instances for testing.
    """
    branch_account_one = BranchAccount.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        account = test_account_one_fixture.get('acc1')
    )

    branch_account_two = BranchAccount.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        account = test_account_one_fixture.get('acc2')
    )

    return {
        "branch_account_one": branch_account_one,
        "branch_account_two": branch_account_two
    }



@pytest.fixture()
def test_company_get_fixture(client, test_company_token_fixture):
    """
    Creates and returns a company detail for testing.
    """
    url = reverse('company-detail', args=[1])
    
    response = client.get(url, HTTP_AUTHORIZATION = f'Bearer: {test_company_token_fixture}')
    logger.info(response.json())
    return response.json()


#=========================================
# Branch Fixture
#=========================================
@pytest.fixture
def create_branch_fixture(test_company_get_fixture):
    """
    Creates and returns Branch instances for testing.
    """
    company = Company.objects.get(id = test_company_get_fixture['id'])

    branch_one =  Branch.objects.create(
        name = "Harare Main",
        company = company,
        code = "HRE-002",
        address = "123 Samora Machel Ave",
        city = "Harare",
        country = "Zimbabwe",
        phone_number = "+263777000000",
        is_active = True,
        manager = None
    )

    branch_two =  Branch.objects.create(
        name = "HMain",
        company = company,
        code = "HRE-003",
        address = "123 Samora Machel",
        city = "Harare",
        country = "Zimbabwe",
        phone_number = "+263777000",
        is_active = True,
        manager = None
    )

    return {
        "one" : branch_one,
        "two" : branch_two
    }


#######################################
# Loan Fixture
#######################################
from datetime import date
from datetime import timedelta

@pytest.fixture()
def create_loan_fixture(create_user):
    return Loan.objects.create(
        borrower = create_user,
        loan_amount = 1000.00,
        interest_rate = 0.05,
        start_date = date.today(),
        end_date = date.today() + timedelta(days=20),
        issued_by = create_user,
    )


##################
#
####################

@pytest.fixture
def create_entity_account_fixture(client, test_user_token, test_account_fixture, test_customer_fixture, create_loan_fixture, test_supplier_fixture):
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
    
    return

#=========================================
# Expense Fixture
#=========================================
@pytest.fixture
def test_expense_fixture(test_company_fixture, create_branch, create_user):
    return Expense.objects.create(
        company = test_company_fixture,
        branch = create_branch,
        expense_number = Expense.generate_expense_number(Expense),
        category = "TRAVEL",
        amount = 10000.00,
        incurred_by = create_user
    )