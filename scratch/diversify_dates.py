import os
import django
import random
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hani_shop.settings')
django.setup()

from reviews.models import Order
from django.utils import timezone

def diversify_dates():
    orders = list(Order.objects.all().order_by('id'))
    now = timezone.now()
    for i, o in enumerate(reversed(orders)):
        # Spread orders over the last 15 days, 3 orders per day approximately
        days_ago = i // 3
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        o.created_at = now - timedelta(days=days_ago, hours=random_hours, minutes=random_minutes)
        o.save()
    print(f"Updated {len(orders)} orders with diverse dates.")

if __name__ == "__main__":
    diversify_dates()
