from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, generics
from .serializers import ProductSerializer, PlanSerializer, \
    SubscriptionSerializer, UsageRecordSerializer
from .models import Product, Plan, Subscription
from users.models import customer, Vendor, VendorStaff

User = get_user_model()


class ProductMangementViewSet(viewsets.ModelViewSet):
    """
    APIs to handle the product management
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
class PlanManagementViewSet(viewsets.ModelViewSet):
    """
    APIs to  handile the plans and planfeature
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PlanSerializer
    queryset = Plan.objects.filter(is_active=True)

  
class ReadOnlyPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allows view plans (list and retrieve only).
    """
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [IsAuthenticated]
    
class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    APIs to handle the subscription management
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    queryset = Subscription.objects.all()
    
    def create(self, request, *args, **kwargs):
        """
        Function to create a new subscription.
        """
        user = request.user
        vendor = Vendor.objects.filter(
            staff_vendor__user = user
        ).select_related('staff_vendor').first()
        try:
            customer_obj = customer.objects.filter(
                user = user,
                vendor = vendor
            ).first()
        except customer.DoesNotExist:
            return Response(
                {"message": "User is not a customer of this vendor"}
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=customer_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        """
        Function to list subscriptions.
        """
        user = request.user
        vendor = Vendor.objects.filter(
            staff_vendor__user = user
        ).select_related('staff_vendor').first()
        
        try:
            customer_obj = customer.objects.filter(
                user = user,
                vendor = vendor
            ).first()
        except customer.DoesNotExist:
            return Response(
                {"message": "User is not a customer of this vendor"}
            )
            
        queryset = self.get_queryset().filter(customer=customer_obj)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        Function to retrieve a subscription.
        """
        user = request.user
        vendor = Vendor.objects.filter(
            staff_vendor__user = user
        ).select_related('staff_vendor').first()
        
        try:
            customer_obj = customer.objects.filter(
                user = user,
                vendor = vendor
            ).first()
        except customer.DoesNotExist:
            return Response(
                {"message": "User is not a customer of this vendor"}
            )
        queryset = self.get_queryset().filter(customer=customer_obj)
        
        try:
            subscription = queryset.get(pk=pk)
        except Subscription.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def update(self, request, *args, **kwargs):
        subscription = self.get_object()
        serializer = self.get_serializer(subscription, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if 'plan' in request.data:
            new_plan = serializer.validated_data['plan']
            if new_plan.product.vendor != subscription.customer.vendor:
                return Response(
                    {"message": "Can't assign plan from diffrent vendor"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        self.perform_update(serializer)
        return Response(serializer.data)
    

class UsageRecordCreateAPI(generics.CreateAPIView):
    serializer_class = UsageRecordSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    