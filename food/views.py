from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Kitchen, Food, Order
from .serializers import KitchenSerializer, FoodSerializer, OrderSerializer

class KitchenViewSet(viewsets.ModelViewSet):
    queryset = Kitchen.objects.all().order_by('-rating')
    serializer_class = KitchenSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['name', 'owner_name']
    ordering_fields = ['rating', 'total_orders', 'created_at']


class FoodViewSet(viewsets.ModelViewSet):
    serializer_class = FoodSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["name", "kitchen_name", "description"]
    ordering_fields = ["price", "delivery_time", "created_at", "kitchen__rating"]
    ordering = ["created_at"]

    def get_queryset(self):
        qs = Food.objects.select_related("kitchen").all()
        
        # Filter by delivery status
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(delivery_status=status)

        # Sort by query param
        ordering = self.request.query_params.get("ordering")
        if ordering == "rating":
            qs = qs.order_by("-kitchen__rating")
        elif ordering in ["price", "delivery_time", "created_at"]:
            qs = qs.order_by(ordering)
        return qs


class KitchenPaginator(PageNumberPagination):
    page_size = 20
    page_size_query_param = "pageSize"
    max_page_size = 50


class FoodPaginator(PageNumberPagination):
    page_size = 50
    page_size_query_param = "pageSize"
    max_page_size = 20


@api_view(["GET"])
def homepage(request):
    from rest_framework.pagination import PageNumberPagination

    kitchen_paginator = PageNumberPagination()
    kitchen_paginator.page_size = 10

    kitchens = Kitchen.objects.all().order_by("-rating")
    kitchen_page = kitchen_paginator.paginate_queryset(kitchens, request)
    kitchen_data = KitchenSerializer(kitchen_page, many=True, context={"request": request}).data

    # Attach foods under each kitchen
    for k in kitchen_data:
        foods = Food.objects.filter(kitchen=k["id"]).order_by("-created_at")
        food_paginator = PageNumberPagination()
        food_paginator.page_size = 5
        food_page = food_paginator.paginate_queryset(foods, request)
        k["foods"] = FoodSerializer(food_page, many=True, context={"request": request}).data

    return kitchen_paginator.get_paginated_response(kitchen_data)


@api_view(["POST"])
def rate_kitchen(request, kitchen_id):
    try:
        kitchen = Kitchen.objects.get(id=kitchen_id)
    except Kitchen.DoesNotExist:
        return Response({"error": "Kitchen not found"}, status=404)

    rating = request.data.get("rating")
    if rating is None:
        return Response({"error": "Rating required"}, status=400)

    rating = float(rating)
    if not 1 <= rating <= 5:
        return Response({"error": "Rating must be 1–5"}, status=400)

    # Simple average (can improve with real rating count)
    kitchen.rating = (kitchen.rating + rating) / 2
    kitchen.save()

    return Response({"message": "Rating submitted", "newRating": kitchen.rating})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user
    food_id = request.data.get("food")
    quantity = int(request.data.get("quantity", 1))

    try:
        food = Food.objects.get(id=food_id)
    except Food.DoesNotExist:
        return Response({"error": "Food not found"}, status=404)

    if user.profile.role == "seller" and str(food.kitchen.owner_id) == str(user.id):
        return Response({"error": "Sellers cannot order their own food"}, status=403)

    order = Order.objects.create(
        user=user,
        food=food,
        quantity=quantity,
        total_price=food.price * quantity
    )

    return Response(OrderSerializer(order).data, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def seller_orders(request):
    """Get all orders for seller's kitchens"""
    user = request.user
    
    seller_kitchens = Kitchen.objects.filter(owner_id=str(user.id))
    
    seller_foods = Food.objects.filter(kitchen__in=seller_kitchens)
    
    orders = Order.objects.filter(food__in=seller_foods).order_by("-created_at")
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Update order status - only by seller who owns the kitchen"""
    user = request.user
    
    try:
        order = Order.objects.select_related('food__kitchen').get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)
    
    # Check if user owns the kitchen
    if str(order.food.kitchen.owner_id) != str(user.id):
        return Response({"error": "Not authorized"}, status=403)
    
    new_status = request.data.get("status")
    if not new_status:
        return Response({"error": "Status required"}, status=400)
    
    if new_status not in dict(Order.STATUS_CHOICES):
        return Response({"error": "Invalid status"}, status=400)
    
    order.status = new_status
    order.save()
    
    # Update kitchen total_orders when delivered
    if new_status == "delivered":
        order.food.kitchen.total_orders += 1
        order.food.kitchen.save()
    
    return Response(OrderSerializer(order).data)