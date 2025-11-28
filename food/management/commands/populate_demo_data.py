import random
import requests
from io import BytesIO
from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from food.models import Kitchen, Food
from user.models import UserProfile

fake = Faker()

class Command(BaseCommand):
    help = "Generate demo seller users, many kitchens, and lots of rice foods from TheMealDB"

    def handle(self, *args, **kwargs):
        NUM_SELLERS = 12
        KITCHENS_PER_SELLER = 4
        FOOD_MIN = 8
        FOOD_MAX = 12

        # Only "rice" meals
        self.stdout.write("\nFetching rice meals from TheMealDB...\n")
        all_foods = []

        try:
            resp = requests.get("https://www.themealdb.com/api/json/v1/1/search.php?s=rice", timeout=10)
            meals = resp.json().get("meals", [])
            if meals:
                for meal in meals:
                    if meal.get("strMeal") and meal.get("strMealThumb"):
                        all_foods.append({
                            "name": meal["strMeal"],
                            "image_url": meal["strMealThumb"]
                        })
        except Exception as e:
            self.stdout.write(f"Failed to fetch rice meals: {e}")

        if not all_foods:
            self.stdout.write("No rice meals found! Using placeholder images instead.")
            all_foods = [{"name": f"Rice Dish {i+1}", "image_url": "https://via.placeholder.com/200"} for i in range(20)]

        self.stdout.write(f"Collected {len(all_foods)} rice meals.\n")

        for _ in range(NUM_SELLERS):
            email = fake.unique.email()
            password = "demoSeller123"

            seller = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            profile_name = fake.name()
            UserProfile.objects.create(
                uid=seller,
                name=profile_name,
                role="seller"
            )

            self.stdout.write(f"Seller created → {email}")

            for i in range(KITCHENS_PER_SELLER):
                kitchen_name = fake.company() + " Kitchen"
                kitchen = Kitchen.objects.create(
                    name=kitchen_name,
                    owner_name=profile_name,
                    owner_id=seller.id,
                    rating=round(random.uniform(3.5, 5), 2),
                    total_orders=random.randint(10, 300)
                )

                self.stdout.write(f"  Kitchen #{i+1} → {kitchen.name}")

                num_foods = random.randint(FOOD_MIN, FOOD_MAX)
                for f in range(num_foods):
                    meal = random.choice(all_foods)
                    try:
                        img_r = requests.get(meal["image_url"], timeout=10)
                        food_img = File(BytesIO(img_r.content), name=f"food_{random.randint(1000,9999)}.jpg")

                        Food.objects.create(
                            name=meal["name"],
                            kitchen=kitchen,
                            price=round(random.uniform(120, 650), 2),
                            delivery_time=random.randint(10, 90),
                            description=fake.text(140),
                            quantity=random.randint(1, 20),
                            image=food_img
                        )
                    except Exception as e:
                        self.stdout.write(f"Failed to create food image: {e}")
                        continue

            self.stdout.write("")

        self.stdout.write(self.style.SUCCESS("\nDemo database populated successfully with rice meals!\n"))
