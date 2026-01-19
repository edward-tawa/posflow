from django.contrib import admin
from taxes.models import *

admin.site.register(FiscalDevice)
admin.site.register(FiscalDocument)
admin.site.register(FiscalInvoiceItem)
admin.site.register(FiscalInvoice)
admin.site.register(FiscalisationResponse)