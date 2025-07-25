from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import Vendor,  customer, VendorStaff
from products.models import Product, Plan, Subscription, UsageLog, Invoice

class Command(BaseCommand):
    """Create default user roles and assign permissions"""

    def handle(self, *args, **kwargs):
        platform_group, _ = Group.objects.get_or_create(name='platform_admin')
        platform_perms = Permission.objects.filter(content_type__model__in=[
            'vendor', 'user', 'product', 'plan', 'subscription', 'customer',
            'vendorstaff', 'UsageLog', 'invoice'
        ])
        platform_group.permissions.set(platform_perms)
        self.stdout.write(self.style.SUCCESS('Platform Admin group set up'))

        vendor_group, _ = Group.objects.get_or_create(name='vendor_admin')
        vendor_perms = Permission.objects.filter(content_type__model__in=[
            'product', 'plan', 'subscription', 'customer',
            'vendorstaff', 'UsageLog', 'invoice'
        ])
        vendor_group.permissions.set(vendor_perms)
        self.stdout.write(self.style.SUCCESS('Vendor Admin group set up'))
        
        vendor_staff_group, _ = Group.objects.get_or_create(name='vendor_staff')
        vendor_staff_perms = Permission.objects.filter(content_type__model__in=[
            'subscription', 'invoice', 'UsageLog', 'customer'
        ])
        vendor_staff_group.permissions.set(vendor_staff_perms)
        self.stdout.write(self.style.SUCCESS('Vendor Staff group set up'))
        
        customer_group, _ = Group.objects.get_or_create(name='customer')
        customer_perms = Permission.objects.filter(content_type__model__in=[
            'subscription', 'invoice'
        ])
        customer_group.permissions.set(customer_perms)
        self.stdout.write(self.style.SUCCESS('Customer group set up'))

        self.stdout.write(self.style.SUCCESS(
            'All user roles and permissions have been created.'))
