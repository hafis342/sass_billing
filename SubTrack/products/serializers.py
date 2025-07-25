from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Plan, PlanFeature, Subscription, UsageLog

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    """
    serializer for product data
    """
    
    class Meta:
        model = Product
        fields = '__all__'
 
class PlanFeatureSerializer(serializers.ModelSerializer):
    """
    serializer for plan feature management
    """
    
    class Meta:
        model = PlanFeature
        fields = ('id', 'name', 'is_active')
        extra_kwargs = {
            'id': {'read_only': False}
        }
          
        
class PlanSerializer(serializers.ModelSerializer):
    """
    serializers for plan managemnt
    """
    plan_features = PlanFeatureSerializer(many=True)
    
    class Meta:
        model = Plan
        fields = (
            'id', 'product', 'name', 'price',  'billing_cycle', 
            'billing_interval', 'unit', 'price_per_unit', 
            'trial_quota', 'is_metered', 'trial_days', 'plan_features'
                 )
      
    def create(self, validated_data: dict) -> Plan:
        """Function to create a new plan and its features.
        Args:
            validated_data (dict): The validated data for creating the plan.
        """
        plan_features_data = validated_data.pop('plan_features', [])
        plan = Plan.objects.create(**validated_data)

        for feature_data in plan_features_data:
            feature_serializer = PlanFeatureSerializer(data=feature_data)
            feature_serializer.is_valid(raise_exception=True)
            feature_serializer.save(plan=plan)

        return plan
    
    def update(self, instance: Plan, validated_data: dict) -> Plan:
        """Function to update an existing plan and its features.
        Args:
            instance (Plan): The plan instance to be updated.
            validated_data (dict): The validated data for updating the plan.
        """
        import pdb;pdb.set_trace()
        features_data = validated_data.pop('plan_features', [])
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if features_data:
            for feature_data in features_data:
                feature_id = feature_data.get('id')
                
                if feature_id:
                    # Update existing feature
                    try:
                        feature = instance.plan_features.get(id=feature_id)
                        feature_serializer = PlanFeatureSerializer(
                            feature, data=feature_data, partial=True)
                        feature_serializer.is_valid(raise_exception=True)
                        feature_serializer.save()
                    except PlanFeature.DoesNotExist:
                        raise serializers.ValidationError(
                            f"Feature with id {feature_id} does not exist.")
                else:
                    # Create new feature
                    feature_serializer = PlanFeatureSerializer(data=feature_data)
                    feature_serializer.is_valid(raise_exception=True)
                    feature_serializer.save(plan=instance)
            
        return instance
    
    def to_representation(self, instance: Plan) -> dict:
        """
        function to representation function to get the plan features
        """
        active_features = instance.plan_features.filter(is_active=True)
        plan_feature_serializer = PlanFeatureSerializer(active_features, many=True)
        data = super().to_representation(instance)
        data['plan_features'] = plan_feature_serializer.data
        
        return data

   
class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for subscription data
    """
    class Meta:
        model = Subscription
        fields = ('id', 'customer', 'plan', 'start_date', 
                  'end_date', 'trial_end_date', 'status')
        

class UsageRecordSerializer(serializers.ModelSerializer):
    subscription_plan = serializers.CharField(
        source='subscription.plan.name', read_only=True
        )
    customer_email = serializers.CharField(
        source='subscription.customer.user.email', read_only=True
        )
    
    class Meta:
        model = UsageLog
        fields = '__all__'
    
    def validate(self, data):
        subscription = data.get('subscription')
        if subscription.plan.is_metered:
            raise serializers.ValidationError(
                "Usage can only be recorded for metered plans"
                )
        return data        
       