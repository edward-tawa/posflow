from django.contrib import admin
from accounts.models import *

admin.site.register(Account)
admin.site.register(BankAccount)
admin.site.register(BranchAccount)
admin.site.register(CashAccount)
admin.site.register(CustomerAccount)
admin.site.register(EmployeeAccount)
admin.site.register(ExpenseAccount)
admin.site.register(LoanAccount)
admin.site.register(PurchasesAccount)
admin.site.register(PurchasesReturnsAccount)
admin.site.register(SalesAccount)
admin.site.register(SalesReturnsAccount)
admin.site.register(SupplierAccount)
admin.site.register(WriteOffAccount)