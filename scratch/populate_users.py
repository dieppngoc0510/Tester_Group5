import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hani_shop.settings')
django.setup()

from django.contrib.auth.models import User
from reviews.models import Product, Order, OrderItem

names = [
    "Nguyễn Văn An", "Trần Thị Bình", "Lê Hoàng Cường", "Phạm Minh Dung", 
    "Hoàng Thanh Hà", "Phan Ngọc Hân", "Đỗ Kim Liên", "Vũ Bảo Nam", 
    "Đặng Quốc Thái", "Bùi Thu Thảo", "Ngô Gia Bảo", "Lý Hải Đăng"
]

for name in names:
    username = name.lower().replace(" ", "") + str(random.randint(10, 99))
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, password='password123', first_name=name)
        # Create at least one order for each new user
        order = Order.objects.create(user=user, status=random.choice(['pending', 'shipping', 'completed']), total_amount=random.randint(100000, 2000000))
        print(f"Created user: {username}")

print("Done populating users and orders.")
