from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    slug = models.SlugField(unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã sản phẩm")
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Giá")
    old_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="Giá cũ")
    image_name = models.CharField(max_length=100, verbose_name="Tên file ảnh (trong static)")
    colors = models.JSONField(default=list, blank=True, verbose_name="Danh sách màu (JSON: name, hex)")
    sizes = models.JSONField(default=list, blank=True, verbose_name="Danh sách size (JSON list)")
    categories = models.ManyToManyField(Category, verbose_name="Danh mục")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    stock = models.IntegerField(default=100, verbose_name="Tồn kho")

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name="Giới tính")
    birthdate = models.DateField(blank=True, null=True, verbose_name="Ngày sinh")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Địa chỉ")

    def __str__(self):
        return f"Profile of {self.user.username}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('shipping', 'Đang vận chuyển'),
        ('completed', 'Hoàn thành'),
        ('return', 'Trả hàng/Hoàn tiền'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255) # Lưu tên lại phòng khi sản phẩm bị xóa
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=1)
    selected = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'product', 'color', 'size')

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"
