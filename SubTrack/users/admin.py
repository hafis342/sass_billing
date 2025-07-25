from django.contrib import admin
from .models import User, Vendor, VendorStaff, customer


admin.site.register(User)
admin.site.register(customer)
admin.site.register(Vendor)
admin.site.register(VendorStaff)

    
    
