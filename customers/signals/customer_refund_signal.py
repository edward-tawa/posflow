# from django.dispatch import receiver
# from django.db.models.signals import post_save
# from transactions.models.transaction_model import Transaction
# from customers.services.customer_credit_service import CustomerCreditService



# @receiver(post_save, sender=Transaction)
# def customer_refund(sender, instance, created, **kwargs):
#     """
#     Signal to process customer refund when a Transaction of type 'REFUND' is created.
#     """
#     if not created:
#         return
#     if instance.transaction_category == 'REFUND' and instance.customer:
#         CustomerCreditService.customer_refund(
#             instance.customer,
#             instance
#             )




# this signal has been deprecated in favor of direct service calls within transaction processing logic.