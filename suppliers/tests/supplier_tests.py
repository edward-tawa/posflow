from fixture_tests import *

@pytest.mark.django_db
def test_supplier_urls(client, test_user_token):
    """
    Test Supplier endpoints.
    """
    url = reverse('supplier-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "name": "Mega Supply Corp",
        "email": "sales@megasupply.com",
        "phone_number": "+263771999888",
        "address": "Industrial Site, Bulawayo"
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
def test_purchase_order_urls(client, test_user_token, test_supplier_fixture):
    """
    Test Purchase Order endpoints.
    """
    url = reverse('purchaseorder-list') # Note: 'purchaseorder-list' from provided url conf
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "supplier": test_supplier_fixture.id,
        "order_date": "2024-02-05",
        "expected_delivery": "2024-02-10",
        'quantity_ordered': 12,
        'total_amount': 123
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
def test_purchase_invoice_urls(client, test_user_token, test_supplier_fixture, test_purchase_order_fixture):
    """
    Test Purchase Invoice endpoints.
    """
    url = reverse('purchase-invoice-list')
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "supplier": test_supplier_fixture.id,
        "purchase_order": test_purchase_order_fixture.id,
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
def test_supplier_credit_note_urls(client, test_user_token, test_supplier_fixture):
    """
    Test Supplier Credit Note endpoints.
    """
    url = reverse('supplier-credit-note-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "supplier": test_supplier_fixture.id,
        "amount": "200.00",
        "reason": "Overcharge on Invoice #123"
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201

from decimal import Decimal

@pytest.mark.django_db
def test_purchase_order_item_urls(client, test_user_token, test_purchase_order_fixture, test_product_fixture):
    """
    Test Purchase Order Item endpoints.
    """
    url = reverse('purchaseorderitem-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        'purchase_order': test_purchase_order_fixture.id, 
        'quantity': 5, 
        'unit_price': 2.45,
        'product': test_product_fixture.id, 
        'total_amount': Decimal(2.45 * 5)
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
def test_purchase_order_item_attachment_actions(client, test_user_token):
    """
    Test the explicit attach/detach actions for Purchase Order Items.
    """
    pk = 1
    # 1. Attach to Order
    url_attach = reverse('purchaseorderitem-attach-to-order', args=[pk])
    client.post(url_attach, {"order_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Detach from Order
    url_detach = reverse('purchaseorderitem-detach-from-order', args=[pk])
    client.post(url_detach, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_purchase_invoice_item_attachment_actions(client, test_user_token):
    """
    Test the explicit attach/detach actions for Purchase Invoice Items.
    """
    pk = 1
    # 1. Attach to Invoice
    url_attach = reverse('purchase-invoice-item-attach-to-invoice', args=[pk])
    client.post(url_attach, {"invoice_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Detach from Invoice
    url_detach = reverse('purchase-invoice-item-detach-from-invoice', args=[pk])
    client.post(url_detach, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_purchase_return_item_attachment_actions(client, test_user_token):
    """
    Test the explicit attach/detach actions for Purchase Return Items.
    """
    pk = 1
    # 1. Attach to Return
    url_attach = reverse('purchase-return-item-attach-return', args=[pk])
    client.post(url_attach, {"return_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Detach Return
    url_detach = reverse('purchase-return-item-detach-return', args=[pk])
    client.post(url_detach, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_supplier_credit_note_item_actions(client, test_user_token):
    """
    Test the explicit actions for Supplier Credit Note Items.
    """
    pk = 1
    # 1. Attach Credit Note
    url_attach = reverse('supplier-credit-note-item-attach-credit-note', args=[pk])
    client.post(url_attach, {"note_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Detach Credit Note
    url_detach = reverse('supplier-credit-note-item-detach-credit-note', args=[pk])
    client.post(url_detach, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Update Quantity & Price
    client.post(reverse('supplier-credit-note-item-update-quantity', args=[pk]), {"quantity": 10}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-credit-note-item-update-unit-price', args=[pk]), {"price": "50.00"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_supplier_explicit_assignments(client, test_user_token):
    """
    Test the explicit assignment endpoints for Suppliers found in your URL list.
    """
    pk = 1
    # 1. Assign Company
    url_assign = reverse('supplier-assign-company', args=[pk])
    client.post(url_assign, {"company_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Unassign Company
    url_unassign = reverse('supplier-unassign-company', args=[pk])
    client.post(url_unassign, {"company_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Attach Branch
    url_attach = reverse('supplier-attach-branch', args=[pk])
    client.post(url_attach, {"branch_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 4. Detach Branch
    url_detach = reverse('supplier-detach-branch', args=[pk])
    client.post(url_detach, {"branch_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_purchase_allocation_validate(client, test_user_token):
    """
    Test Purchase Payment Allocation validation.
    """
    pk = 1
    client.post(reverse('purchase-payment-allocation-validate-allocation', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_supplier_note_item_actions(client, test_user_token):
    """
    Test Supplier Credit/Debit Note Item actions.
    """
    item_pk = 1

    # 1. Credit Note Item Actions
    client.post(reverse('supplier-credit-note-item-attach-credit-note', args=[item_pk]), {"note_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-credit-note-item-detach-credit-note', args=[item_pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-credit-note-item-update-quantity', args=[item_pk]), {"quantity": 5}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-credit-note-item-update-unit-price', args=[item_pk]), {"price": "10.00"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Debit Note Item Actions
    client.post(reverse('supplier-debit-note-item-update-status', args=[item_pk]), {"status": "PROCESSED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_supplier_granular_actions(client, test_user_token):
    """
    Test granular Supplier actions (Assign, Attach, Detach).
    """
    pk = 1
    # 1. Company/Branch Assignments
    client.post(reverse('supplier-assign-company', args=[pk]), {"company_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-unassign-company', args=[pk]), {"company_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-attach-branch', args=[pk]), {"branch_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-detach-branch', args=[pk]), {"branch_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Status Update
    client.post(reverse('supplier-update-status', args=[pk]), {"status": "ACTIVE"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_purchase_item_actions(client, test_user_token):
    """
    Test Purchase Order/Invoice/Return Item specific actions.
    """
    item_pk = 1
    
    # 1. Purchase Order Item Actions
    client.post(reverse('purchaseorderitem-attach-to-order', args=[item_pk]), {"order_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('purchaseorderitem-detach-from-order', args=[item_pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('purchaseorderitem-update-status', args=[item_pk]), {"status": "RECEIVED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Purchase Invoice Item Actions
    # Note: CRUD for this might have been missed, checking actions first
    client.post(reverse('purchase-invoice-item-attach-to-invoice', args=[item_pk]), {"invoice_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('purchase-invoice-item-detach-from-invoice', args=[item_pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Purchase Return Item Actions
    client.post(reverse('purchase-return-item-attach-return', args=[item_pk]), {"return_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('purchase-return-item-detach-return', args=[item_pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('purchase-return-item-update-status', args=[item_pk]), {"status": "RETURNED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_purchase_order_workflow_actions(client, test_user_token):
    """
    Test Purchase Order workflow actions.
    """
    pk = 1
    # 1. Approve Order
    client.post(reverse('purchaseorder-approve-order', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_purchase_invoice_workflow_actions(client, test_user_token):
    """
    Test Purchase Invoice workflow actions.
    """
    pk = 1
    # 1. Approve & Status
    client.post(reverse('purchase-invoice-approve', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('purchase-invoice-update-status', args=[pk]), {"status": "PAID"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Detach Supplier
    client.post(reverse('purchase-invoice-detach-from-supplier', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_purchase_return_workflow_actions(client, test_user_token):
    """
    Test Purchase Return workflow actions.
    """
    pk = 1
    # 1. Attach/Detach Supplier
    client.post(reverse('purchase-return-attach-supplier', args=[pk]), {"supplier_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('purchase-return-detach-supplier', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Update Status
    client.post(reverse('purchase-return-update-status', args=[pk]), {"status": "COMPLETED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_supplier_note_actions(client, test_user_token):
    """
    Test Supplier Debit/Credit Note actions.
    """
    pk = 1
    # 1. Debit Note Actions
    client.post(reverse('supplier-debit-note-attach-supplier', args=[pk]), {"supplier_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-debit-note-detach-supplier', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-debit-note-update-status', args=[pk]), {"status": "APPROVED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Credit Note Actions
    client.post(reverse('supplier-credit-note-attach-supplier', args=[pk]), {"supplier_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-credit-note-detach-supplier', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('supplier-credit-note-update-status', args=[pk]), {"status": "APPROVED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_supplier_bulk_import(client, test_user_token):
    """
    Test Supplier Bulk Import/Export.
    """
    # 1. Import
    url_import = reverse('supplier-bulk-import')
    client.post(url_import, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Export CSV
    url_export = reverse('supplier-export-csv')
    response = client.get(url_export, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response)
    assert response.status_code == 200

@pytest.mark.django_db
def test_supplier_debit_note_urls(client, test_user_token, test_supplier_fixture):
    """
    Test Supplier Debit Note endpoints.
    """
    url = reverse('supplier-debit-note-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "supplier": test_supplier_fixture.id,
        "amount": "100.00",
        "reason": "Returned Goods Debit"
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
def test_supplier_debit_note_item_urls(client, test_user_token, test_supplier_debit_note_fixture):
    """
    Test Supplier Debit Note Item endpoints.
    """
    url = reverse('supplier-debit-note-item-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "supplier_debit_note": test_supplier_debit_note_fixture.id,
        "quantity": 12,
        "unit_price": 5.50,
        "description": "Item 1",
        "amount": "50.00"
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
def test_supplier_credit_note_item_urls(client, test_user_token, test_supplier_credit_note_fixture):
    """
    Test Supplier Credit Note Item endpoints.
    """
    url = reverse('supplier-credit-note-item-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "supplier_credit_note": test_supplier_credit_note_fixture.id,
        "description": "Correction Item",
        "amount": "20.00",
        "quantity": 5,
        "unit_price": 5
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
def test_purchase_return_item_urls(client, test_user_token, test_product_fixture, test_purchase_return_fixture):
    """
    Test Purchase Return Item endpoints.
    """
    url = reverse('purchase-return-item-list')

    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "purchase_return": test_purchase_return_fixture.id,
        "product": test_product_fixture.id,
        "quantity": 5,
        "unit_price": 12
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
def test_purchase_payment_urls(client, test_user_token, test_supplier_fixture, test_payment_fixture, test_purchase_invoice_fixture):
    """
    Test Purchase Payment endpoints.
    """
    url = reverse('purchase-payment-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    data = {
        "supplier": test_supplier_fixture.id,
        "payment": test_payment_fixture.id,
        "purchase_invoice": test_purchase_invoice_fixture.id,
        "amount_paid": "500.00",
        "method": "BANK",
        "payment_date": "2024-02-20"
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
def test_purchase_payment_allocation_urls(client, test_user_token, test_supplier_fixture, test_purchase_invoice_fixture, test_purchase_payment_fixture):
    """
    Test Purchase Payment Allocation endpoints.
    """
    url = reverse('purchase-payment-allocation-list')
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    data = {
        "purchase_payment": test_purchase_payment_fixture.id,
        "purchase_invoice": test_purchase_invoice_fixture.id,
        "supplier": test_supplier_fixture.id,
        "amount_allocated": "500.00"
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201
