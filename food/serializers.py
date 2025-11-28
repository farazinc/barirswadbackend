from rest_framework import serializers
from django.conf import settings
from .models import Food, Kitchen, Order

class KitchenSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()

    class Meta:
        model = Kitchen
        fields = [
            "id", "name", "owner_id", "owner_name",
            "image", "rating", "total_orders",
            "created_at", "imageUrl"
        ]

    def get_imageUrl(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else settings.MEDIA_URL + obj.image.name
        return None


class FoodSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()
    kitchen = serializers.PrimaryKeyRelatedField(queryset=Kitchen.objects.all())
    kitchenName = serializers.CharField(source="kitchen_name", read_only=True)
    deliveryTime = serializers.IntegerField(source="delivery_time")
    deliveryStatus = serializers.ChoiceField(
        source="delivery_status",
        choices=Food.DELIVERY_CHOICES,
        required=False,
        default="pending"
    )

    class Meta:
        model = Food
        fields = [
            "id", "name", "kitchen", "kitchenName",
            "price", "description", "quantity",
            "deliveryTime", "deliveryStatus",
            "image", "created_at", "imageUrl"
        ]
        extra_kwargs = {
            "image": {"required": False, "allow_null": True},
        }

    def get_imageUrl(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else settings.MEDIA_URL + obj.image.name
        return None

    def create(self, validated_data):
        # Get kitchen from validated data
        kitchen = validated_data.get('kitchen')
        
        # Auto-populate kitchen_name from the kitchen object
        validated_data['kitchen_name'] = kitchen.name
        
        # Set default delivery_status if not provided
        if 'delivery_status' not in validated_data:
            validated_data['delivery_status'] = 'pending'
        
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source="food.name", read_only=True)
    kitchen_name = serializers.CharField(source="food.kitchen_name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "food",
            "food_name",
            "kitchen_name",
            "quantity",
            "total_price",
            "status",
            "created_at"
        ]