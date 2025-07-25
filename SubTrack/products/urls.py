from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'product', views.ProductMangementViewSet, basename='product')
router.register(r'plan', views.PlanManagementViewSet, basename='plan')

urlpatterns = [
    path('', include(router.urls)),
    path('usage-log/', views.UsageRecordCreateAPI.as_view())
]
