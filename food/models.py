from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Kitchen(models.Model):
    name = models.CharField(max_length=120)
    owner_id = models.CharField(max_length=50)
    owner_name = models.CharField(max_length=120)
    image = models.ImageField(upload_to="kitchens/", null=True, blank=True)
    rating = models.FloatField(default=0)
    total_orders = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def imageUrl(self):
        return f"/media/{self.image.name}" if self.image else None


class Food(models.Model):
    DELIVERY_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("preparing", "Preparing"),
        ("ontheway", "On The Way"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    name = models.CharField(max_length=150)
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name="foods")
    kitchen_name = models.CharField(max_length=120)
    price = models.FloatField()
    description = models.TextField()
    quantity = models.IntegerField()

    delivery_time = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
        db_index=True,
    )

    delivery_status = models.CharField(
        max_length=20, choices=DELIVERY_CHOICES, default="pending", db_index=True
    )

    image = models.ImageField(upload_to="foods/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def imageUrl(self):
        return f"/media/{self.image.name}" if self.image else None



class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("preparing", "Preparing"),
        ("ontheway", "On The Way"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"