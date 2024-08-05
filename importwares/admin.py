from django.contrib import admin

from .models import Cargo, Supplier, Category, WarehousePallet, AssignedPallet, RackPlace


# Register your models here.


admin.site.register(Cargo)
admin.site.register(Supplier)
admin.site.register(Category)
admin.site.register(WarehousePallet)

admin.site.register(RackPlace)
admin.site.register(AssignedPallet)