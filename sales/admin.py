from django.contrib import admin
from sales.models import *

admin.site.register(DeliveryNote)
admin.site.register(DeliveryNoteItem)
admin.site.register(Sale)
admin.site.register(SalesInvoiceItem)
admin.site.register(SalesInvoice)
admin.site.register(SalesOrderItem)
admin.site.register(SalesOrder)
admin.site.register(SalesPayment)
admin.site.register(SalesQuotationItem)
admin.site.register(SalesQuotation)
admin.site.register(SalesReceiptItem)
admin.site.register(SalesReceipt)
admin.site.register(SalesReturnItem)
admin.site.register(SalesReturn)