from django.contrib import admin
from payments.models import *

admin.site.register(Expense)
admin.site.register(PaymentAllocation)
admin.site.register(PaymentMethod)
admin.site.register(Payment)
admin.site.register(PaymentReceiptItem)
admin.site.register(PaymentReceipt)
admin.site.register(Refund)