from django.contrib import admin
from transactions.models import *

admin.site.register(TransactionItem)
admin.site.register(Transaction)