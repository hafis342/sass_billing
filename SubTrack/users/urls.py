from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'vendor', views.VendorManagement, basename='vendor')
router.register(r'vendor-staff', views.VendorStaffManagement, basename='vendor-staff')
router.register(r'customer', views.CustomerManagement, basename='customer')


urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.LoginView.as_view(), name = 'login' ),
]
