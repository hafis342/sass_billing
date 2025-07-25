from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from .models import Vendor, VendorStaff, customer
from django.db import transaction

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs: dict) -> dict:
        """
        Validation function to check the user credentials.
        """
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid username or password")
        attrs['user'] = user
        return attrs
    
class VendorSerializer(serializers.ModelSerializer):
    """
    Serializer for Vendor model.
    """
    class Meta:
        model = Vendor
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        
        extra_kwargs = {'password': {'write_only': True}}
        
class VendorStaffSerializer(serializers.ModelSerializer):
    """
    Serializer for VendorStaff Management.
    """
    user = UserSerializer()
    
    class Meta:
        model = VendorStaff
        fields = '__all__'
    
    @transaction.atomic   
    def create(self, validated_data: dict) -> VendorStaff:
        """
        Create new vendor staff
        """
        user_data = validated_data.pop('user')
        vendor = validated_data.pop('vendor')
        is_admin = validated_data.get('is_admin', False)
        
        try:
            User.objects.get(username=user_data['username'])
        except User.DoesNotExist:
            user = User.objects.create(**user_data)
            
        if VendorStaff.objects.filter(
            user__username=user_data['username'], vendor=vendor).exists():
            raise serializers.ValidationError(
                "User is already a staff member of this vendor")
    
        vendor_staff = VendorStaff.objects.create(
            user=user, vendor=vendor, is_admin=is_admin)
        group_name = 'vendor_admin' if is_admin else 'vendor_staff'
        group = Group.objects.get_or_create(name=group_name)[0]
        user.groups.add(group)
        
        return vendor_staff
    
    
class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer model.
    """
    user = UserSerializer()
    
    class Meta:
        model = customer
        fields = '__all__'
        
    def validate(self, attrs: dict) -> dict:
        user = attrs.get('user')
        vendor = attrs.get('vendor')
        
        if customer.objects.filter(user=user, vendor=vendor).exists():
            raise serializers.ValidationError(
                "User is already a customer of this vendor")
        if not vendor or not user:
            raise serializers.ValidationError("Vendor and User are required")
        
        return attrs
        
    def create(self, validated_data: dict) -> customer:
        """
        Create new customer
        """
        user_data = validated_data.pop('user')
        print(user_data)
        try:
            User.objects.get(username=user_data['username'])
        except User.DoesNotExist:
            user = User.objects.create_user(**user_data)
    
        customer_obj = customer.objects.create(
            user=user, vendor=validated_data['vendor'])
        group = Group.objects.get_or_create(name='customer')[0]
        user.groups.add(group)
        
        return customer_obj