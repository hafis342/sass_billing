from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets
from .serilizers import LoginSerializer, VendorSerializer, VendorStaffSerializer, CustomerSerializer
from .models import Vendor, VendorStaff, customer
from django.contrib.auth.models import Group

User = get_user_model()


class LoginView(APIView):
    """
    API to handile the user login
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request) -> Response:
        """
        Handiles the user Login
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'roles': [group.name for group in user.groups.all()],
                
            }}, status=status.HTTP_200_OK)
        
        
class VendorManagement(viewsets.ModelViewSet):
    """
    APIs to handle the vendor management
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VendorSerializer
    queryset = Vendor.objects.all()


class VendorStaffManagement(viewsets.ModelViewSet):
    """
    APIs to handle the vendor staff management 
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VendorStaffSerializer
    queryset = VendorStaff.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        vendor_id = self.request.query_params.get('vendor_id', None)
        if vendor_id is not None:
            queryset = queryset.filter(vendor__vendor_id=vendor_id)
        return queryset
        

   
class CustomerManagement(viewsets.ModelViewSet):
    """
    APIs to handle the customer management
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    queryset = customer.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        vendor_id = self.request.query_params.get('vendor_id', None)
        if vendor_id is not None:
            queryset = queryset.filter(vendor__vendor_id=vendor_id)
        return queryset
    
    

