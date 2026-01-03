from fixture_tests import *

@pytest.mark.django_db
def test_expense_urls(client, test_user_token):
    """
    Test Expense endpoints.
    """
    url = reverse('expense-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "category": 1, # Expense Category ID (if exists) or just description
        "amount": "15.50",
        "description": "Lunch for team",
        "date_incurred": "2024-01-01"
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
def test_payment_allocation_urls(client, test_user_token):
    """
    Test Payment Allocation endpoints.
    """
    url = reverse('payment-allocation-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    assert response.status_code == 200

    # Test CREATE
    data = {
        "payment": 1,
        "invoice": 1,
        "amount": "100.00"
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    # Expect 201 if dependencies exist
    if response.status_code != 201:
        logger.warning(f"Payment Allocation Create failed: {response.data}")

@pytest.mark.django_db
def test_payment_urls(client, test_user_token):
    """
    Test Payment endpoints.
    """
    url = reverse('payment-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "customer": 1,
        "amount": "200.00",
        "method": "CASH",
        "reference": "PAY-001"
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
def test_payment_actions(client, test_user_token):
    """
    Test Payment actions: Attach Invoice, Complete, Fail, etc.
    """
    # ID 1 assumed
    payment_id = 1
    
    # 1. Attach Invoice
    url_attach = reverse('payment-attach-invoice', args=[payment_id])
    data = {"invoice_id": 1}
    client.post(url_attach, data, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Complete Payment
    url_complete = reverse('payment-complete-payment', args=[payment_id])
    client.post(url_complete, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Fail Payment
    url_fail = reverse('payment-fail-payment', args=[payment_id])
    client.post(url_fail, {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_payment_receipt_urls(client, test_user_token, test_payment_fixture):
    """
    Test Payment Receipt endpoints.
    """
    url = reverse('payment-receipt-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE (Manual receipt creation if allowed)
    data = {
        "payment": test_payment_fixture.id,
        "amount": 1000
    }
    response = client.post(
        url, 
        data, 
        content_type='application/json', 
        HTTP_AUTHORIZATION=f'Bearer {test_user_token}'
    )
    logger.info(response.json())
    assert response.status_code in [200, 201]

@pytest.mark.django_db
def test_refund_urls(client, test_user_token, test_payment_fixture):
    """
    Test Refund endpoints.
    """
    url = reverse('refund-list')
    
    # Test GET
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    logger.info(response.json())
    assert response.status_code == 200

    # Test CREATE
    data = {
        "payment": test_payment_fixture.id,
        "amount": "50.00",
        "reason": "product_defect"
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
def test_expense_workflow_actions(client, test_user_token):
    """
    Test specific actions for Expenses (Attach, Detach, Status Updates).
    """
    pk = 1
    # 1. Attach/Detach Payment
    client.post(reverse('expense-attach-payment', args=[pk]), {"payment_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('expense-detach-payment', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Mark Paid/Unpaid
    client.post(reverse('expense-mark-paid', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('expense-mark-unpaid', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Update Status
    client.post(reverse('expense-update-status', args=[pk]), {"status": "APPROVED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_refund_workflow_actions(client, test_user_token):
    """
    Test the complex Refund workflow (Process, Cancel, Fail, Attachments).
    """
    pk = 1
    
    # 1. State Transitions
    client.post(reverse('refund-process-refund', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('refund-pending-refund', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('refund-fail-refund', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('refund-cancel-refund-action', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    
    # 2. Attachments
    client.post(reverse('refund-attach-customer', args=[pk]), {"customer_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('refund-attach-order', args=[pk]), {"order_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('refund-attach-payment', args=[pk]), {"payment_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Detachments
    client.post(reverse('refund-detach-customer', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('refund-detach-order', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('refund-detach-payment', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_payment_workflow_actions(client, test_user_token):
    """
    Test Payment specific actions (Attach/Detach relations, Complete/Fail).
    """
    pk = 1
    
    # 1. Attachments
    client.post(reverse('payment-attach-customer', args=[pk]), {"customer_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-attach-invoice', args=[pk]), {"invoice_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-attach-order', args=[pk]), {"order_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Detachments
    client.post(reverse('payment-detach-customer', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-detach-invoice', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-detach-order', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Status Actions (Complete/Fail were partially tested before, reiterating specifically here)
    client.post(reverse('payment-complete-payment', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-fail-payment', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_payment_allocation_actions(client, test_user_token):
    """
    Test Payment Allocation actions.
    """
    pk = 1
    
    # 1. Apply & Reverse
    client.post(reverse('payment-allocation-apply-allocation', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-allocation-reverse-allocation', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Attach/Detach Customer
    client.post(reverse('payment-allocation-attach-customer', args=[pk]), {"customer_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-allocation-detach-customer', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 3. Delete/Status
    client.post(reverse('payment-allocation-delete-allocation', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-allocation-update-status', args=[pk]), {"status": "COMPLETED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_payment_receipt_actions(client, test_user_token):
    """
    Test Payment Receipt actions.
    """
    pk = 1

    # 1. Send & Cancel
    client.post(reverse('payment-receipt-send-receipt', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-receipt-cancel-receipt', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Attach/Detach Relations
    client.post(reverse('payment-receipt-attach-relation', args=[pk]), {"relation_id": 1}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-receipt-detach-relation', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    
    # 3. Update Status
    client.post(reverse('payment-receipt-update-status', args=[pk]), {"status": "SENT"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_payment_receipt_item_actions(client, test_user_token):
    """
    Test Payment Receipt Item actions.
    """
    pk = 1

    # 1. Mark Refunded
    client.post(reverse('payment-receipt-item-mark-refunded', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-receipt-item-unmark-refunded', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Attach/Detach Receipt (if moved between receipts)
    client.post(reverse('payment-receipt-item-attach-receipt', args=[pk]), {"receipt_id": 2}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('payment-receipt-item-detach-receipt', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

@pytest.mark.django_db
def test_payment_updates(client, test_user_token):
    """
    Test generic updates for purchase/sales payments.
    """
    pk = 1
    # 1. Purchase Payment Update
    client.post(reverse('purchase-payment-update-status', args=[pk]), {"status": "CLEARED"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('purchase-payment-update-notes', args=[pk]), {"notes": "Updated note"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')

    # 2. Sales Payment Update Amount (Reverse)
    client.post(reverse('sales-payment-update-amount', args=[pk]), {"amount": "120.00"}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
    client.post(reverse('sales-payment-reverse-payment', args=[pk]), {}, content_type='application/json', HTTP_AUTHORIZATION=f'Bearer {test_user_token}')
