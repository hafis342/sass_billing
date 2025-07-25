from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from users.models import DateTimeBaseModel, Vendor, User, customer
from dateutil.relativedelta import relativedelta


class Product(DateTimeBaseModel):
    """
    Model representing  product data.
    """
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self) -> str:
        return f"{self.name} - {self.vendor.name}"

  
class Plan(DateTimeBaseModel):
    """
    Model repesnting product plan data.
    """
    BILLING_CYCLES = (
        ('day', 'Day'),
        ('month', 'Month'),
        ('year', 'Year'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_plans')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_interval = models.PositiveIntegerField(default=1)
    billing_cycle = models.CharField(choices=BILLING_CYCLES, default='month')
    unit = models.CharField(max_length=50, null=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    trial_quota = models.IntegerField(default=0)
    is_metered = models.BooleanField(default=False)
    trial_days = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    
    def __str__(self) -> str:
        return f"{self.name} - {self.product.name}"
    
    def get_trail_end_date(self, from_date: datetime = None) -> datetime:
        """
        Function to get the trail end data
        Args:
            from_date (datetime): Date from which the trial period starts. If None, current date will be use
        Returns:
            datetime: Trial period end data
        """
        from_date = from_date or timezone.now().date()
        return from_date + timedelta(days=self.trial_days)
  
    def get_billing_date(self, from_date: datetime = None) -> datetime:
        """
        Function to get the billing date
        Args:
            from_date (datetime): Billing period start date. If None, current date will be use
        Retruns:
            datetime: Returns billing end date
        """
        from_date = from_date or timezone.now().date()
        billing_cycle = self.billing_cycle
        billing_interval = self.billing_interval
        
        if billing_cycle == 'day':
            return from_date + timedelta(days=billing_interval)
        elif billing_cycle == 'month':
            return from_date + relativedelta(months=billing_interval)
        elif billing_cycle == 'year':
            return from_date + relativedelta(year=billing_interval)
        return from_date

  
class PlanFeature(DateTimeBaseModel):
    """
    Model representing plan feature data.
    """
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_features')
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return f"{self.name} - {self.plan.name}"
  
class Subscription(DateTimeBaseModel):
    """
    Model to represent user subscription data.
    """
    SUBSCRIPTION_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('trialing', 'Trialing')
    )
    customer = models.ForeignKey(
        customer, on_delete=models.CASCADE, related_name='customer_subcription')
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name='plan_subscription')
    status = models.CharField(choices=SUBSCRIPTION_STATUS)
    start_date = models.DateField()
    end_date = models.DateField()
    trial_end_date = models.DateField()
    
    def __str__(self) -> str:
        return f"{self.customer.username} - {self.plan.name}"
    
    def save(self, *args, **kwargs) -> None:
        """
        Auto save the subscription start date, end date, trial_end_date
        and status, when a new subscripton is created.
        """
        if not self.pk:
            current_date = timezone.now().date()
            
            if self.plan.trial_days > 0:
                self.trial_end_date = self.plan.get_trail_end_date(current_date)
                self.status = 'trialing'
            else:
                self.trial_end_date = current_date
                self.status = 'active'
                
            self.start_date = current_date
            self.end_date = self.plan.get_billing_date(current_date)
        super().save(*args, **kwargs)
            
        
class UsageLog(DateTimeBaseModel):
    """
    Model to represent feature usage log data.
    """
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name='subscription_usage')
    feature_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    log_date = models.DateField()
    is_billed = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.feature_name} - {self.subscription.customer.username}"    

class Invoice(DateTimeBaseModel):
    """
    Model to represent invoice data.
    """
    INVOICE_STATUS = (
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('overdue', 'Overdue')
    )
    
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='customer_invoice')
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name='subscription_invoice')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(choices=INVOICE_STATUS)
    invoice_date = models.DateField()
    pdf_url = models.URLField()
    due_date = models.DateField()
    
    def __str__(self) -> str:
        return f"{self.customer.username} - {self.subscription.plan.name}"
    
        
    