from fixture_tests import *

@pytest.mark.django_db
def test_sales_quotation_urls(client, test_user_token, test_customer_fixture):
    """
    Test Sales Quotation endpoints.
    """
    url = reverse('sales-quotation-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "customer": test_customer_fixture.id,
        "date": "2024-02-01",
        "valid_until": "2024-02-15",
        "status": "draft"
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
def test_sales_order_urls(client, test_user_token, test_customer_fixture):
    """
    Test Sales Order endpoints.
    """
    url = reverse('sales-order-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "customer": test_customer_fixture.id,
        "status": "draft"
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
def test_sales_invoice_urls(client, test_user_token, test_customer_fixture):
    """
    Test Sales Invoice endpoints.
    """
    url = reverse('sales-invoice-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "customer": test_customer_fixture.id,
        "invoice_date": "2024-02-02",
        "due_date": "2024-03-02"
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
def test_sales_invoice_actions(client, test_user_token):
    """
    Test Sales Invoice specific actions like Apply Discount, Mark Issued.
    """
    # ID 1 assumed
    invoice_id = 1
    
    # 1. Apply Discount
    url_discount = reverse('sales-invoice-apply-discount', args=[invoice_id])
    data = {"discount_amount": "10.00"}
    client.post(url_discount, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Mark as Issued
    url_issue = reverse('sales-invoice-mark-as-issued', args=[invoice_id])
    client.post(url_issue, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Void Invoice
    url_void = reverse('sales-invoice-void-invoice', args=[invoice_id])
    client.post(url_void, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_delivery_note_urls(client, test_user_token, test_customer_fixture, test_sale_order_fixture):
    """
    Test Delivery Note endpoints.
    """
    url = reverse('delivery-note-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "customer": test_customer_fixture.id,
        "sales_order": test_sale_order_fixture.id,
        "delivery_address": "123 Main St, Harare",
        "status": "pending"
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
def test_sales_return_urls(client, test_user_token, test_customer_fixture, test_sale_order_fixture):
    """
    Test Sales Return endpoints.
    """
    url = reverse('sales-return-list')
     
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "customer": test_customer_fixture.id,
        "sale_order": test_sale_order_fixture.id,
        "return_date": "2024-02-10",
        "reason": "defective_product",
        "total_amount": 1000
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
def test_sales_payment_apply_action(client, test_user_token):
    """
    Test the missing 'sales-payment-apply-payment' endpoint.
    """
    # Path: sales-payments/apply/ (No ID in path usually, ID in body)
    url = reverse('sales-payment-apply-payment')
    data = {
        "payment_id": 1,
        "invoice_ids": [1, 2]
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_delivery_note_attachments_extra(client, test_user_token):
    """
    Double check attachments for delivery notes.
    """
    pk = 1
    # We tested attach-order/receipt, ensuring attach-invoice isn't needed or is covered by standard updates.
    # Re-verifying 'delivery-note-update-status' with valid payload
    url = reverse('delivery-note-update-status', args=[pk])
    client.post(url, {"status": "DISPATCHED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_invoice_item_bulk_create(client, test_user_token):
    """
    Test the specific bulk create endpoint for Sales Invoice Items.
    """
    url = reverse('sales-invoice-item-bulk-create-items')
    data = {
        "invoice_id": 1,
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ]
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_receipt_item_bulk_create(client, test_user_token):
    """
    Test the specific bulk create endpoint for Sales Receipt Items.
    """
    url = reverse('sales-receipt-item-bulk-create-items')
    data = {
        "receipt_id": 1,
        "items": [
            {"product_id": 1, "quantity": 1}
        ]
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_delivery_note_item_actions(client, test_user_token):
    """
    Test Delivery Note Item actions.
    """
    item_pk = 1
    client.post(reverse('delivery-note-item-attach', args=[item_pk]), {"note_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('delivery-note-item-detach', args=[item_pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_invoice_item_extra(client, test_user_token):
    """
    Test missing Sales Invoice Item actions.
    """
    # Mark Invoice Paid via Item endpoint (rare but in your list)
    client.post(reverse('sales-invoice-item-mark-invoice-as-paid'), {"invoice_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    
@pytest.mark.django_db
def test_sales_receipt_extra(client, test_user_token):
    """
    Test missing Sales Receipt actions.
    """
    pk = 1
    # Void Receipt
    client.post(reverse('sales-receipt-void-receipt', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_receipt_item_urls(client, test_user_token, test_sale_receipt_fixture, test_product_fixture):
    """
    Test Sales Receipt Item endpoints.
    """
    url = reverse('sales-receipt-item-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "sales_receipt": test_sale_receipt_fixture.id,
        "product": test_product_fixture.id,
        "quantity": 1,
        "unit_price": "100.00",
        "tax_rate": 0.05
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
def test_sales_return_item_urls(client, test_user_token, test_product_fixture, test_sale_return_fixture):
    """
    Test Sales Return Item endpoints.
    """
    url = reverse('sales-return-item-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "sales_return": test_sale_return_fixture.id,
        "product": test_product_fixture.id,
        "quantity": 1,
        "condition": "Damaged",
        "unit_price": 20.98,
        "tax_rate": 0.05
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
def test_sales_item_actions(client, test_user_token):
    """
    Test Sales Quotation/Return Item specific actions.
    """
    item_pk = 1

    # 1. Sales Quotation Item Actions
    client.post(reverse('sales-quotation-item-attach-invoice', args=[item_pk]), {"invoice_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('sales-quotation-item-attach-quotation', args=[item_pk]), {"quotation_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('sales-quotation-item-detach-invoice', args=[item_pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Sales Return Item Actions
    client.post(reverse('sales-return-item-attach-to-return', args=[item_pk]), {"return_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('sales-return-item-update-status', args=[item_pk]), {"status": "RESTOCKED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_order_workflow_actions(client, test_user_token):
    """
    Test Sales Order specific workflow actions.
    """
    pk = 1
    # 1. Attach/Detach Invoice
    client.post(reverse('sales-order-attach-invoice', args=[pk]), {"invoice_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    
    # 2. Update Status
    client.post(reverse('sales-order-update-status', args=[pk]), {"status": "CONFIRMED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Bulk Items (if not fully tested in batch 8)
    data = {"items": [{"product": 1, "quantity": 10}]}
    client.post(reverse('sales-order-bulk-items', args=[pk]), data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_quotation_workflow_actions(client, test_user_token):
    """
    Test Sales Quotation actions.
    """
    pk = 1
    # 1. Attach/Detach Customer
    client.post(reverse('sales-quotation-attach-customer', args=[pk]), {"customer_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('sales-quotation-detach-customer', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Update Status
    client.post(reverse('sales-quotation-update-status', args=[pk]), {"status": "ACCEPTED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_return_workflow_actions(client, test_user_token):
    """
    Test Sales Return workflow actions.
    """
    pk = 1
    # 1. Update Status
    client.post(reverse('sales-return-update-status', args=[pk]), {"status": "PROCESSED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_delivery_note_workflow_actions(client, test_user_token):
    """
    Test Delivery Note workflow actions.
    """
    pk = 1
    # 1. Attachments
    client.post(reverse('delivery-note-attach-order', args=[pk]), {"order_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('delivery-note-attach-receipt', args=[pk]), {"receipt_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Detachments
    client.post(reverse('delivery-note-detach-receipt', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Update Status
    client.post(reverse('delivery-note-update-status', args=[pk]), {"status": "DELIVERED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_invoice_bulk_items(client, test_user_token):
    """
    Test Bulk Create Items for Sales Invoice.
    """
    url = reverse('sales-invoice-item-bulk-create-items')
    data = {
        "invoice": 1,
        "items": [
            {"product": 1, "quantity": 1},
            {"product": 2, "quantity": 2}
        ]
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_receipt_bulk_items(client, test_user_token):
    """
    Test Bulk Create Items for Sales Receipt.
    """
    url = reverse('sales-receipt-item-bulk-create-items')
    data = {
        "receipt": 1,
        "items": [
            {"product": 1, "quantity": 1}
        ]
    }
    client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_sales_quotation_item_urls(client, test_user_token, test_product_fixture, test_sale_quotation_fixture):
    """
    Test Sales Quotation Item endpoints.
    """
    url = reverse('sales-quotation-item-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "sales_quotation": test_sale_quotation_fixture.id,
        "product": test_product_fixture.id,
        "product_name": test_product_fixture.name,
        "quantity": 10,
        'unit_price': 100, 
        'tax_rate': 0.05
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
def test_delivery_note_item_urls(client, test_user_token, test_delivery_note_fixture, test_product_fixture):
    """
    Test Delivery Note Item endpoints.
    """
    url = reverse('delivery-note-item-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "delivery_note": test_delivery_note_fixture.id,
        "product": test_product_fixture.id,
        'product_name': test_product_fixture.name,
        'quantity': 3, 
        'unit_price': 20.50, 
        'tax_rate': 0.05
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code == 201


############################################################################
########################################################################################

# ==========================================
# DELIVERY NOTES
# ==========================================

# @pytest.mark.django_db
# def test_delivery_note_endpoints(client, test_user_token):
#     """
#     Test Delivery Note List, Detail, and Status Update.
#     [Source: 19]
#     """
#     url = reverse('delivery-note-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     data = None
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 201

#     # Detail
#     url_detail = reverse('delivery-note-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Update Status
#     url_status = reverse('delivery-note-update-status', kwargs={'pk': 1})
#     client.post(url_status, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# @pytest.mark.django_db
# def test_delivery_note_attachments(client, test_user_token):
#     """
#     Test Delivery Note Attachments (Order, Receipt) and Item management.
#     [Source: 19]
#     """
#     data = None

#     # Attach Order
#     url_attach_order = reverse('delivery-note-attach-order', kwargs={'pk': 1})
#     client.post(url_attach_order, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Attach/Detach Receipt
#     client.post(reverse('delivery-note-attach-receipt', kwargs={'pk': 1}), data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     client.post(reverse('delivery-note-detach-receipt', kwargs={'pk': 1}), data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Delivery Note Items (Generic List/Detail)
#     url_items = reverse('delivery-note-item-list')
#     client.get(url_items, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Attach/Detach specific items (Item level)
#     url_item_attach = reverse('delivery-note-item-attach', kwargs={'pk': 1})
#     client.post(url_item_attach, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     url_item_detach = reverse('delivery-note-item-detach', kwargs={'pk': 1})
#     client.post(url_item_detach, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# # ==========================================
# # SALES INVOICES
# # ==========================================

# @pytest.mark.django_db
# def test_sales_invoice_endpoints(client, test_user_token):
#     """
#     Test Sales Invoice List, Detail, and Actions (Discount, Issue, Void).
#     [Source: 20, 21]
#     """
#     url = reverse('sales-invoice-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     data = None
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 201

#     # Detail
#     url_detail = reverse('sales-invoice-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Apply Discount
#     url_discount = reverse('sales-invoice-apply-discount', kwargs={'pk': 1})
#     client.post(url_discount, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Mark Issued
#     url_issued = reverse('sales-invoice-mark-as-issued', kwargs={'pk': 1})
#     client.post(url_issued, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Void Invoice
#     url_void = reverse('sales-invoice-void-invoice', kwargs={'pk': 1})
#     client.post(url_void, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# @pytest.mark.django_db
# def test_sales_invoice_item_endpoints(client, test_user_token):
#     """
#     Test Sales Invoice Items and Bulk Creation.
#     [Source: 20]
#     """
#     url = reverse('sales-invoice-item-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     # Bulk Create Items
#     url_bulk = reverse('sales-invoice-item-bulk-create-items')
#     data = None
#     response = client.post(
#         url_bulk, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
#     )
#     assert response.status_code == 201

#     # Mark Invoice Paid (at item level context?)
#     url_mark_paid = reverse('sales-invoice-item-mark-invoice-as-paid')
#     client.post(url_mark_paid, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')



# # ==========================================
# # SALES ORDERS
# # ==========================================

# @pytest.mark.django_db
# def test_sales_order_endpoints(client, test_user_token):
#     """
#     Test Sales Order List, Detail, and Status Update.
#     [Source: 21, 22]
#     """
#     url = reverse('sales-order-list')
    
#     # Test GET
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     # Test CREATE
#     data = None
#     response = client.post(
#         url, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 201

#     # Detail
#     url_detail = reverse('sales-order-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Update Status
#     url_status = reverse('sales-order-update-status', kwargs={'pk': 1})
#     client.post(url_status, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# @pytest.mark.django_db
# def test_sales_order_actions(client, test_user_token):
#     """
#     Test Sales Order actions: Attach Invoice, Bulk Items.
#     [Source: 21]
#     """
#     data = None
    
#     # Attach Invoice
#     url_attach = reverse('sales-order-attach-invoice', kwargs={'pk': 1})
#     response = client.post(
#         url_attach, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
#     )
#     logger.info(response.json())
#     assert response.status_code == 201

#     # Bulk Items
#     url_bulk = reverse('sales-order-bulk-items', kwargs={'pk': 1})
#     response = client.post(
#         url_bulk, 
#         data, 
#         content_type='application/json', 
#         HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
#     )
#     assert response.status_code == 201


# # ==========================================
# # SALES PAYMENTS
# # ==========================================

# @pytest.mark.django_db
# def test_sales_payment_endpoints(client, test_user_token):
#     """
#     Test Sales Payment List, Detail, and Apply/Reverse actions.
#     [Source: 22]
#     """
#     url = reverse('sales-payment-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     data = None
#     response = client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 201

#     # Detail
#     url_detail = reverse('sales-payment-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Apply Payment (General)
#     url_apply = reverse('sales-payment-apply-payment')
#     client.post(url_apply, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Reverse Payment
#     url_reverse = reverse('sales-payment-reverse-payment', kwargs={'pk': 1})
#     client.post(url_reverse, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Update Amount
#     url_amount = reverse('sales-payment-update-amount', kwargs={'pk': 1})
#     client.post(url_amount, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# # ==========================================
# # SALES QUOTATIONS
# # ==========================================

# @pytest.mark.django_db
# def test_sales_quotation_endpoints(client, test_user_token):
#     """
#     Test Sales Quotation List, Detail, and Workflow.
#     [Source: 23, 24]
#     """
#     url = reverse('sales-quotation-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     data = None
#     response = client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 201

#     # Detail
#     url_detail = reverse('sales-quotation-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Update Status
#     url_status = reverse('sales-quotation-update-status', kwargs={'pk': 1})
#     client.post(url_status, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Attach/Detach Customer
#     client.post(reverse('sales-quotation-attach-customer', kwargs={'pk': 1}), data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     client.post(reverse('sales-quotation-detach-customer', kwargs={'pk': 1}), data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# @pytest.mark.django_db
# def test_sales_quotation_item_endpoints(client, test_user_token):
#     """
#     Test Sales Quotation Items and attachments.
#     [Source: 22, 23]
#     """
#     url = reverse('sales-quotation-item-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     data = None
    
#     # Detail
#     url_detail = reverse('sales-quotation-item-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Attachments
#     url_att_inv = reverse('sales-quotation-item-attach-invoice', kwargs={'pk': 1})
#     client.post(url_att_inv, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     url_att_quo = reverse('sales-quotation-item-attach-quotation', kwargs={'pk': 1})
#     client.post(url_att_quo, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    
#     url_det_inv = reverse('sales-quotation-item-detach-invoice', kwargs={'pk': 1})
#     client.post(url_det_inv, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# # ==========================================
# # SALES RECEIPTS
# # ==========================================

# @pytest.mark.django_db
# def test_sales_receipt_endpoints(client, test_user_token):
#     """
#     Test Sales Receipt List, Detail, and Void.
#     [Source: 23]
#     """
#     url = reverse('sales-receipt-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     data = None
#     response = client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 201

#     # Detail
#     url_detail = reverse('sales-receipt-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Void Receipt
#     url_void = reverse('sales-receipt-void-receipt', kwargs={'pk': 1})
#     client.post(url_void, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# @pytest.mark.django_db
# def test_sales_receipt_items(client, test_user_token):
#     """
#     Test Sales Receipt Items and Bulk Create.
#     [Source: 25]
#     """
#     url = reverse('sales-receipt-item-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     # Bulk Create
#     data = None
#     url_bulk = reverse('sales-receipt-item-bulk-create-items')
#     response = client.post(url_bulk, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 201

#     # Detail
#     url_detail = reverse('sales-receipt-item-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# # ==========================================
# # SALES RETURNS
# # ==========================================

# @pytest.mark.django_db
# def test_sales_return_endpoints(client, test_user_token):
#     """
#     Test Sales Return List, Detail, and Status.
#     [Source: 24]
#     """
#     url = reverse('sales-return-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     data = None
#     response = client.post(url, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 201

#     # Detail
#     url_detail = reverse('sales-return-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Update Status
#     url_status = reverse('sales-return-update-status', kwargs={'pk': 1})
#     client.post(url_status, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')


# @pytest.mark.django_db
# def test_sales_return_item_endpoints(client, test_user_token):
#     """
#     Test Sales Return Items.
#     [Source: 25]
#     """
#     # Note: Using the list name. If 'sales-order-items' uses the same name in your conf, this test hits that.
#     url = reverse('sales-return-item-list')
#     response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
#     assert response.status_code == 200

#     data = None
    
#     # Detail
#     url_detail = reverse('sales-return-item-detail', kwargs={'pk': 1})
#     client.put(url_detail, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Attach to Return
#     url_attach = reverse('sales-return-item-attach-to-return', kwargs={'pk': 1})
#     client.post(url_attach, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

#     # Update Status
#     url_status = reverse('sales-return-item-update-status', kwargs={'pk': 1})
#     client.post(url_status, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')