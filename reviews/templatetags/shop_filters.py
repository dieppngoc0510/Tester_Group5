import unicodedata
from django import template

register = template.Library()

@register.filter
def format_price(value):
    try:
        return f"{value:,.0f} đ".replace(",", ".")
    except (ValueError, TypeError):
        return value

@register.filter
def generate_username(user):
    # Lấy firstname, nếu không có thì lấy chuỗi rỗng
    name = user.first_name if user.first_name else 'user'
    # Bỏ dấu tiếng việt
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    # Loại bỏ khoảng trắng và in thường
    username = ''.join(c for c in name if c.isalnum()).lower()
    
    # Nếu Tên đăng nhập gốc bị rỗng hoặc toàn số, ghép thêm vài chữ số ID
    if username == "user" or not username:
        return f"user_{user.id}"
    return f"{username}{user.id}"
