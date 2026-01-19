from django.contrib import admin
from inventory.models import *

admin.site.register(ProductCategory)
admin.site.register(ProductStock)
admin.site.register(Product)
admin.site.register(StockAdjustment)
admin.site.register(StockMovement)
admin.site.register(StockTakeApproval)
admin.site.register(StockTakeItem)
admin.site.register(StockTake)
admin.site.register(StockWriteOffItem)
admin.site.register(StockWriteOff)