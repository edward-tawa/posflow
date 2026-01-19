from django.contrib import admin
from transfers.models import *

admin.site.register(CashTransfer)
admin.site.register(ProductTransferItem)
admin.site.register(ProductTransfer)
admin.site.register(Transfer)
