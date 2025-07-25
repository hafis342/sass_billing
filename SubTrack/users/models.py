from django.db import models
from django.contrib.auth.models import AbstractBaseUser, AbstractUser


class DateTimeBaseModel(models.Model):
    """
    An abstract base model that provides self-managed "created_at" and "updated_at" fields.

    Attributes:
        created_at (DateTimeField): Timestamp when the object was first created.
        updated_at (DateTimeField): Timestamp when the object was last updated.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-updated_at']
        
class User(DateTimeBaseModel, AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    """
    pass
    
    def __str__(self) -> str:
        return self.email
    
class Vendor(DateTimeBaseModel):
    """
    Model representing a vendor data.
    """
    name = models.CharField(max_length=255)
    vendor_id = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    
    def __str__(self) -> str:
        return self.name
    
    
class VendorStaff(DateTimeBaseModel):
    """
    Model representing a vendor staff member data.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendor_staff_user')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='staff_vendor')
    is_admin = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"{self.user.username} - {self.vendor.name}"

class customer(DateTimeBaseModel):
    """
    Model representing a customer data.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='customer_user', null=True)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name='vendor_customer', null=True)
    
    # class Meta:
    #     unique_together = ('user', 'vendor') 
    
    def __str__(self) -> str:
        return f"{self.user.email}"