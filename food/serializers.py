from rest_framework import serializers
from .models import Food, Kitchen, Order

class KitchenSerializer(serializers.ModelSerializer):
    imageUrl = serializers.ReadOnlyField()

    class Meta:
        model = Kitchen
        fields = [
            "id", "name", "owner_id", "owner_name",
            "image", "rating", "total_orders",
            "created_at", "imageUrl"
        ]


class FoodSerializer(serializers.ModelSerializer):
    imageUrl = serializers.ReadOnlyField()
    kitchen = serializers.PrimaryKeyRelatedField(queryset=Kitchen.objects.all())
    kitchenName = serializers.CharField(source="kitchen_name")
    deliveryTime = serializers.IntegerField(source="delivery_time")
    deliveryStatus = serializers.ChoiceField(
        source="delivery_status", choices=Food.DELIVERY_CHOICES
    )

    class Meta:
        model = Food
        fields = [
            "id", "name", "kitchen", "kitchenName",
            "price", "description", "quantity",
            "deliveryTime", "deliveryStatus",
            "image", "created_at", "imageUrl"
        ]
        extra_kwargs = {"image": {"required": False, "allow_null": True}}


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