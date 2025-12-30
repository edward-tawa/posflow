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
# Debit&Credit Account fixture
#=========================================
@pytest.fixture()
def test_dc_fixture(test_company_fixture, create_branch):
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
    product =  Product(
        company = test_company_fixture,
        branch = create_branch,
        name = 'HP Omen',
        description = 'HIGH PERFOMANCE PC',
        price = 1560,
        product_category = test_product_category_fixture,
        stock = 25
    )

    product.sku =  sku = Product.generate_sku(product)
    product.save()
    return product


#=========================================
# Stocktake Fixture
#=========================================
@pytest.fixture()
def test_stocktake_fixture(create_branch, test_company_fixture, create_user):
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
def test_customer_fixture(create_branch, test_company_fixture, create_user):
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
    return uuid4()


#=========================================
# FiscalInvoice Fixture
#=========================================
@pytest.fixture()
def test_fiscal_invoice_fixture(test_company_fixture, create_branch, test_sale_fixture, test_object_id_fixture):
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