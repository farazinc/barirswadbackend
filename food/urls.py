
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KitchenViewSet, FoodViewSet, create_order, homepage, rate_kitchen, seller_orders, update_order_status,user_orders

router = DefaultRouter()
router.register("kitchens", KitchenViewSet,basename="kitchen")
router.register("foods", FoodViewSet, basename="food")

urlpatterns = [
    path("homepage/", homepage),
    path("kitchens/<int:kitchen_id>/rate/", rate_kitchen),
    path("orders/",create_order),
    path("orders/list/",user_orders) ,
    path("orders/seller/", seller_orders),  
    path("orders/<int:order_id>/status/", update_order_status),
    path("", include(router.urls)),
    
]
