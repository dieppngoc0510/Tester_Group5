from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Category, Product, UserProfile, Order, OrderItem, CartItem
import json

# =================== DỮ LIỆU SẢN PHẨM ===================
PRODUCTS = [
    {
        'id': 1,
        'name': 'Set váy suông tay dài kèm nơ',
        'code': 'SP000000031',
        'price': 400000,
        'old_price': 599000,
        'image': 'sp1.png',
        'colors': [
            {'name': 'Xanh đen', 'hex': '#1a1a3e'},
            {'name': 'Xanh nhạt', 'hex': '#d4e4f7'}
        ],
        'sizes': ['S', 'M', 'L'],
        'category': ['san-pham-moi', 'vay', 'bo-suu-tap']
    },
    {
        'id': 2,
        'name': 'Áo khoác da lộn dáng ngắn',
        'code': 'SP000000032',
        'price': 499000,
        'old_price': 650000,
        'image': 'sp2.png',
        'colors': [
            {'name': 'Đen', 'hex': '#2d2d2d'},
            {'name': 'Nâu', 'hex': '#8B4513'}
        ],
        'sizes': ['S', 'M', 'L'],
        'category': ['san-pham-moi', 'ao', 'bo-suu-tap']
    },
    {
        'id': 3,
        'name': 'Váy midi basic tay xoè',
        'code': 'SP000000033',
        'price': 270000,
        'old_price': 399000,
        'image': 'sp3.png',
        'colors': [
            {'name': 'Trắng', 'hex': '#f5f0e8'},
            {'name': 'Đen', 'hex': '#2d2d2d'}
        ],
        'sizes': ['S', 'M', 'L'],
        'category': ['san-pham-moi', 'vay', 'bo-suu-tap']
    },
    {
        'id': 4,
        'name': 'Áo gile len cổ chữ V',
        'code': 'SP000000034',
        'price': 250000,
        'old_price': 380000,
        'image': 'sp4.png',
        'colors': [
            {'name': 'Đen', 'hex': '#2d2d2d'},
            {'name': 'Đỏ đô', 'hex': '#8B0000'},
            {'name': 'Đỏ', 'hex': '#e53e3e'}
        ],
        'sizes': ['S', 'M', 'L'],
        'category': ['san-pham-moi', 'ao']
    },
    {
        'id': 5,
        'name': 'Áo trễ vai nhung tăm',
        'code': 'SP000000035',
        'price': 180000,
        'old_price': 299000,
        'image': 'sp5.png',
        'colors': [
            {'name': 'Trắng', 'hex': '#f5f0e8'},
            {'name': 'Đen', 'hex': '#2d2d2d'}
        ],
        'sizes': ['S', 'M', 'L'],
        'category': ['san-pham-moi', 'ao', 'bo-suu-tap']
    },
    {
        'id': 6,
        'name': 'Đầm dự tiệc',
        'code': 'SP000000036',
        'price': 250000,
        'image': 'sp6.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'ao']
    },
    {
        'id': 7,
        'name': 'Váy ngắn basic thanh lịch',
        'code': 'SP000000037',
        'price': 320000,
        'image': 'sp7.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'quan']
    },
    {
        'id': 8,
        'name': 'Váy maxi đi biển',
        'code': 'SP000000038',
        'price': 390000,
        'image': 'sp8.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'ao']
    },
    {
        'id': 9,
        'name': 'Áo sơ mi kèm nơ',
        'code': 'SP000000039',
        'price': 450000,
        'image': 'sp9.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'vay']
    },
    {
        'id': 10,
        'name': 'Áo kiểu yếm tiểu thư',
        'code': 'SP000000040',
        'price': 220000,
        'image': 'sp10.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'ao']
    },
    {
        'id': 11,
        'name': 'Quần jean form rộng',
        'code': 'SP000000041',
        'price': 550000,
        'image': 'sp11.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'quan']
    },
    {
        'id': 12,
        'name': 'Áo Cowboys nữ năng động',
        'code': 'SP000000042',
        'price': 350000,
        'image': 'sp12.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'ao']
    },
    {
        'id': 13,
        'name': 'Chân váy dài caro',
        'code': 'SP000000043',
        'price': 290000,
        'image': 'sp13.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'vay']
    },
    {
        'id': 14,
        'name': 'Set áo và quần jean năng động',
        'code': 'SP000000044',
        'price': 420000,
        'image': 'sp14.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'ao']
    },
    {
        'id': 15,
        'name': 'Set váy thể thao',
        'code': 'SP000000045',
        'price': 590000,
        'image': 'sp15.jpg',
        'category': ['san-pham-moi', 'bo-suu-tap-he', 'vay']
    }
]

COUPONS = [
    {'code': 'BLACKFRI50', 'desc': 'Mã giảm 50% cho đơn hàng tối thiểu 999K', 'color': 'red', 'status': 'Đang hoạt động', 'status_color': 'green', 'start': '01/06/2026', 'end': '31/09/2026'},
    {'code': 'FLASH20', 'desc': 'Mã giảm 20% trên tổng giá trị đơn hàng', 'color': 'blue', 'status': 'Đang hoạt động', 'status_color': 'green', 'start': '01/06/2026', 'end': '31/12/2026'},
    {'code': 'FREESHIP', 'desc': 'Mã giảm 30% cho đơn hàng từ 199K', 'color': 'red', 'status': 'Sắp hết hạn', 'status_color': 'red', 'start': '01/06/2026', 'end': '24/10/2026'},
    {'code': 'NEWUSER50', 'desc': 'Mã giảm 50,000đ cho khách hàng mới', 'color': 'red', 'status': 'Đã kết thúc', 'status_color': 'gray', 'start': '01/06/2026', 'end': '24/10/2026'},
]

# =================== HELPER FUNCTIONS ===================
def get_product_by_id(product_id):
    # Thử tìm trong Database trước
    try:
        p_obj = Product.objects.get(id=int(product_id))
        return {
            'id': p_obj.id,
            'name': p_obj.name,
            'code': p_obj.code,
            'price': int(p_obj.price),
            'old_price': int(p_obj.old_price) if p_obj.old_price else None,
            'image': p_obj.image_name,
            # Giữ tương thích với dữ liệu cứng cho colors/sizes nếu chưa chuyển hết sang DB
            'colors': p_obj.colors if p_obj.colors else [{'name': 'Mặc định', 'hex': '#ccc'}],
            'sizes': p_obj.sizes if p_obj.sizes else ['S', 'M', 'L'],
            'category': [cat.slug for cat in p_obj.categories.all()]
        }
    except:
        # Fallback về PRODUCTS list cũ
        for p in PRODUCTS:
            if p['id'] == int(product_id):
                return p
    return None

def get_all_products_from_db():
    db_products = []
    for p_obj in Product.objects.all():
        db_products.append({
            'id': p_obj.id,
            'name': p_obj.name,
            'code': p_obj.code,
            'price': int(p_obj.price),
            'old_price': int(p_obj.old_price) if p_obj.old_price else None,
            'image': p_obj.image_name,
            'colors': p_obj.colors if p_obj.colors else [{'name': 'Mặc định', 'hex': '#ccc'}],
            'sizes': p_obj.sizes if p_obj.sizes else ['S', 'M', 'L'],
            'category': [cat.slug for cat in p_obj.categories.all()]
        })
    return db_products if db_products else PRODUCTS

def format_price(price):
    try:
        return f"{int(price):,.0f} đ".replace(",", ".")
    except:
        return "0 đ"

# =================== VIEWS ===================

def home(request):
    all_p = get_all_products_from_db()
    winter_images = ['sp1.png', 'sp2.png', 'sp3.png', 'sp4.png', 'sp5.png']
    
    # Lấy đúng 5 sản phẩm thu đông làm sản phẩm "Mới" ở trang chủ
    new_products = [p for p in all_p if p['image'] in winter_images]
    # Lấy sản phẩm hè
    summer_products = [p for p in all_p if p['image'] not in winter_images]

    # Tính cart_count: Unique products
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    else:
        cart_count = len(request.session.get('cart', []))
    
    return render(request, 'reviews/home.html', {
        'products': new_products,
        'winter_products': new_products, 
        'summer_products': summer_products,
        'coupons': COUPONS,
        'cart_count': cart_count
    })

def all_products(request, category=None):
    category_names = {
        'san-pham-moi': 'SẢN PHẨM MỚI',
        'bo-suu-tap': 'BỘ SƯU TẬP THU ĐÔNG',
        'bo-suu-tap-he': 'BỘ SƯU TẬP HÈ',
        'ao': 'ÁO',
        'quan': 'QUẦN',
        'vay': 'VÁY'
    }

    all_p = get_all_products_from_db()
    
    if category:
        filtered = [p for p in all_p if category in p['category']]
        filtered = sorted(filtered, key=lambda x: x['id'])
        title = category_names.get(category, 'TẤT CẢ SẢN PHẨM')
        breadcrumb = title
    else:
        filtered = sorted(all_p, key=lambda x: x['id'])
        title = 'TẤT CẢ SẢN PHẨM'
        breadcrumb = 'Tất cả sản phẩm'

    if not filtered: filtered = all_p
    display = filtered

    winter_products = []
    summer_products = []
    if category == 'bo-suu-tap':
        winter_images = ['sp1.png', 'sp2.png', 'sp3.png', 'sp4.png', 'sp5.png']
        winter_products = [p for p in filtered if p['image'] in winter_images]
        summer_products = [p for p in filtered if p['image'] not in winter_images]

    # Unique count
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    else:
        cart_count = len(request.session.get('cart', []))

    return render(request, 'reviews/all_products.html', {
        'products': display,
        'winter_products': winter_products,
        'summer_products': summer_products,
        'category_slug': category,
        'title': title,
        'breadcrumb': breadcrumb,
        'cart_count': cart_count
    })

def search(request):
    query = request.GET.get('q', '').strip().lower()
    if not query: return redirect('home')

    all_p = get_all_products_from_db()
    filtered = [p for p in all_p if query in p['name'].lower() or query in p['code'].lower()]

    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    else:
        cart_count = len(request.session.get('cart', []))

    return render(request, 'reviews/all_products.html', {
        'products': filtered,
        'title': f'Kết quả tìm kiếm: "{query}"',
        'breadcrumb': 'Tìm kiếm',
        'cart_count': cart_count
    })

def product_detail(request, product_id):
    product = get_product_by_id(product_id)
    if not product:
        messages.error(request, 'Sản phẩm không tồn tại!')
        return redirect('home')
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    else:
        cart_count = len(request.session.get('cart', []))

    return render(request, 'reviews/product_detail.html', {
        'product': product,
        'cart_count': cart_count
    })

def add_to_cart(request):
    if request.method == 'POST':
        product_id = int(request.POST.get('product_id', 0))
        color = request.POST.get('color', '')
        size = request.POST.get('size', '')

        product = get_product_by_id(product_id)
        if not product:
            return JsonResponse({'success': False, 'message': 'Sản phẩm không tồn tại'})

        if request.user.is_authenticated:
            p_obj = Product.objects.get(id=product_id)
            item, created = CartItem.objects.get_or_create(
                user=request.user, product=p_obj, color=color, size=size
            )
            if not created:
                item.quantity += 1
                item.save()
            cart_count = CartItem.objects.filter(user=request.user).count()
        else:
            cart = request.session.get('cart', [])
            existing = next((i for i in cart if i['product_id'] == product_id and i['color'] == color and i['size'] == size), None)
            if existing:
                existing['qty'] += 1
            else:
                cart.append({'product_id': product_id, 'color': color, 'size': size, 'qty': 1, 'selected': True})
            request.session['cart'] = cart
            cart_count = len(cart)

        return JsonResponse({
            'success': True,
            'message': 'Đã thêm sản phẩm vào giỏ hàng!',
            'cart_count': cart_count,
            'product_name': product['name'],
            'product_image': product['image']
        })
    return JsonResponse({'success': False})

def cart_data(request):
    items = []
    if request.user.is_authenticated:
        db_items = CartItem.objects.filter(user=request.user)
        for di in db_items:
            product = get_product_by_id(di.product_id)
            if product:
                items.append({
                    'product_id': di.product_id,
                    'name': product['name'],
                    'image': product['image'],
                    'price': product['price'],
                    'price_formatted': format_price(product['price']),
                    'color': di.color,
                    'size': di.size,
                    'qty': di.quantity,
                    'selected': di.selected
                })
    else:
        cart = request.session.get('cart', [])
        for item in cart:
            product = get_product_by_id(item['product_id'])
            if product:
                items.append({
                    'product_id': item['product_id'],
                    'name': product['name'],
                    'image': product['image'],
                    'price': product['price'],
                    'price_formatted': format_price(product['price']),
                    'color': item['color'],
                    'size': item['size'],
                    'qty': item['qty'],
                    'selected': item.get('selected', False)
                })

    selected_total = sum(i['price'] * i['qty'] for i in items if i['selected'])
    selected_count = sum(1 for i in items if i['selected'])

    return JsonResponse({
        'items': items,
        'total': selected_total,
        'total_formatted': format_price(selected_total),
        'count': len(items),
        'selected_count': selected_count
    })

def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        color = data.get('color')
        size = data.get('size')
        action = data.get('action')

        if request.user.is_authenticated:
            if action == 'toggle_all':
                checked = data.get('checked', False)
                CartItem.objects.filter(user=request.user).update(selected=checked)
            else:
                try:
                    item = CartItem.objects.get(user=request.user, product_id=product_id, color=color, size=size)
                    if action == 'increase': 
                        item.quantity += 1
                        item.save()
                    elif action == 'decrease':
                        item.quantity -= 1
                        if item.quantity <= 0: item.delete()
                        else: item.save()
                    elif action == 'delete': item.delete()
                    elif action == 'toggle':
                        item.selected = not item.selected
                        item.save()
                except CartItem.DoesNotExist: pass
        else:
            cart = request.session.get('cart', [])
            if action == 'toggle_all':
                checked = data.get('checked', False)
                for item in cart: item['selected'] = checked
            else:
                for item in cart:
                    if item['product_id'] == product_id and item['color'] == color and item['size'] == size:
                        if action == 'increase': item['qty'] += 1
                        elif action == 'decrease':
                            item['qty'] -= 1
                            if item['qty'] <= 0: cart.remove(item)
                        elif action == 'delete':
                            cart.remove(item)
                        elif action == 'toggle': item['selected'] = not item.get('selected', False)
                        break
            request.session['cart'] = cart
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required(login_url='login')
def checkout(request):
    items = []
    if request.user.is_authenticated:
        db_items = CartItem.objects.filter(user=request.user)
        for di in db_items:
            product = get_product_by_id(di.product_id)
            if product:
                items.append({
                    'product_id': di.product_id,
                    'color': di.color,
                    'size': di.size,
                    'qty': di.quantity,
                    'selected': di.selected,
                    'product': product
                })
    else:
        cart = request.session.get('cart', [])
        for item in cart:
            product = get_product_by_id(item['product_id'])
            if product:
                items.append({**item, 'product': product})

    selected_items = [i for i in items if i['selected']]
    if not selected_items:
        messages.warning(request, 'Vui lòng chọn ít nhất 1 sản phẩm!')
        return redirect('home')

    subtotal = sum(i['product']['price'] * i['qty'] for i in selected_items)

    applied_coupon = request.session.get('applied_coupon', '')
    discount = 50000 if applied_coupon else 0
    shipping = 0
    total = max(0, subtotal - discount + shipping)
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    return render(request, 'reviews/checkout.html', {
        'items': selected_items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'total': total,
        'user': request.user,
        'profile': user_profile,
        'cart_count': len(items)
    })

def confirm_order(request):
    if request.method == 'POST':
        items = []
        if request.user.is_authenticated:
            db_items = CartItem.objects.filter(user=request.user)
            for di in db_items:
                product = get_product_by_id(di.product_id)
                if product:
                    items.append({
                        'product_id': di.product_id, 'color': di.color, 'size': di.size,
                        'qty': di.quantity, 'selected': di.selected, 'price': product['price'], 'name': product['name']
                    })
        else:
            cart = request.session.get('cart', [])
            for item in cart:
                product = get_product_by_id(item['product_id'])
                if product:
                    items.append({**item, 'price': product['price'], 'name': product['name']})

        selected_items = [i for i in items if i.get('selected', False)]
        if not selected_items:
            return redirect('home')

        subtotal = sum(i['price'] * i['qty'] for i in selected_items)
        order_items_data = []
        for i in selected_items:
            order_items_data.append({
                'product_obj': Product.objects.get(id=i['product_id']),
                'name': i['name'], 'color': i['color'], 'size': i['size'],
                'qty': i['qty'], 'price': i['price']
            })

        coupon_code = request.session.get('applied_coupon', '')
        discount = 50000 if coupon_code else 0
        total = max(0, subtotal - discount)

        # Tạo đơn hàng
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            coupon_code=coupon_code,
            discount_amount=discount,
            status='shipping'  # Mặc định là đang vận chuyển sau khi đặt
        )

        # Tạo chi tiết đơn hàng
        for item in order_items_data:
            OrderItem.objects.create(
                order=order,
                product=item['product_obj'],
                product_name=item['name'],
                color=item['color'],
                size=item['size'],
                quantity=item['qty'],
                price=item['price']
            )

        # Xóa các sản phẩm đã đặt khỏi giỏ hàng và xóa mã giảm giá
        if request.user.is_authenticated:
            CartItem.objects.filter(user=request.user, selected=True).delete()
        else:
            new_cart = [item for item in cart if not item.get('selected', False)]
            request.session['cart'] = new_cart
        
        request.session['applied_coupon'] = ''
        
        return redirect('order_success')
    return redirect('home')

def order_success(request):
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(user=request.user).count()
    else:
        cart_count = len(request.session.get('cart', []))
    
    return render(request, 'reviews/order_success.html', {
        'cart_count': cart_count
    })

@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=identifier, password=password)
        
        if user is None:
            profile = UserProfile.objects.filter(phone=identifier).first()
            if profile:
                user = authenticate(request, username=profile.user.username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Đồng bộ giỏ hàng từ Session sang DB khi login
            session_cart = request.session.get('cart', [])
            for s_item in session_cart:
                p_obj = Product.objects.get(id=s_item['product_id'])
                db_item, created = CartItem.objects.get_or_create(
                    user=user, product=p_obj, color=s_item['color'], size=s_item['size']
                )
                if not created:
                    db_item.quantity += s_item['qty']
                    db_item.save()
                else:
                    db_item.quantity = s_item['qty']
                    db_item.selected = s_item.get('selected', True)
                    db_item.save()
            request.session['cart'] = [] # Xóa guest cart sau khi sync
            
            messages.success(request, f'Xin chào, {user.first_name if user.first_name else user.username}!')
            response = redirect('home')
            # Set marker cookie for JS to detect fresh login
            response.set_cookie('just_logged_in', '1', max_age=30) 
            return response
        else:
            messages.error(request, 'Tên đăng nhập/Số điện thoại hoặc mật khẩu không chính xác!')
    return render(request, 'reviews/login.html')

@never_cache
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        address = request.POST.get('address', '').strip()
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập này đã tồn tại!')
        elif UserProfile.objects.filter(phone=phone).exists():
            messages.error(request, 'Số điện thoại này đã được sử dụng!')
        else:
            user = User.objects.create_user(username=username, password=password)
            user.first_name = fullname
            user.email = email
            user.save()
            
            # Tạo profile và lưu thông tin ngay lập tức vào DB
            UserProfile.objects.create(
                user=user,
                phone=phone,
                address=address
            )
            
            auth_login(request, user)
            messages.success(request, f'Đăng ký thành công! Xin chào, {username}!')
            response = redirect('home')
            response.set_cookie('just_logged_in', '1', max_age=30)
            return response
    return render(request, 'reviews/register.html')

def logout(request):
    auth_logout(request)
    if not request.GET.get('silent'):
        messages.success(request, 'Đăng xuất thành công!')
    return redirect('home')

def apply_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code', '')
        request.session['applied_coupon'] = code
        return JsonResponse({'success': True, 'message': f'Đã áp dụng mã {code}'})
    return JsonResponse({'success': False})
def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    # Get or create UserProfile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        birthdate = request.POST.get('birthdate', '')
        address = request.POST.get('address', '').strip()
        gender = request.POST.get('gender', 'nu')

        # Cập nhật thông tin cốt lõi vào Database
        request.user.first_name = first_name
        request.user.email = email
        request.user.save()

        # Lưu các trường bổ sung vào UserProfile DB
        user_profile.phone = phone
        user_profile.address = address
        if birthdate: 
            user_profile.birthdate = birthdate
        else:
            user_profile.birthdate = None
        user_profile.gender = gender
        user_profile.save()
        
        messages.success(request, 'Cập nhật thông tin hồ sơ thành công!')
        return redirect('profile')

    # Xử lý GET request (Hiển thị từ DB)
    birthdate = ""
    if user_profile.birthdate:
        birthdate = user_profile.birthdate.strftime('%Y-%m-%d')
    else:
        birthdate = "2005-02-08" # Ngày mặc định tạm hiển thị
    gender = user_profile.gender if user_profile.gender else 'nu'
    address = user_profile.address if user_profile.address else ''
    
    return render(request, 'reviews/profile.html', {
        'user': request.user,
        'profile': user_profile,
        'birthdate': birthdate,
        'gender': gender,
        'address': address,
        'cart_count': sum(item['qty'] for item in request.session.get('cart', []))
    })

def orders(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    status_filter = request.GET.get('status', 'all')
    
    user_orders = Order.objects.filter(user=request.user)
    if status_filter != 'all':
        user_orders = user_orders.filter(status=status_filter)
    
    return render(request, 'reviews/orders.html', {
        'user': request.user,
        'status': status_filter,
        'user_orders': user_orders,
        'cart_count': sum(item['qty'] for item in request.session.get('cart', []))
    })

def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    if request.method == 'POST':
        # Demo logic cho đổi mật khẩu
        messages.success(request, 'Đổi mật khẩu thành công!')
        return redirect('profile')
        
    return render(request, 'reviews/change_password.html', {
        'user': request.user,
        'cart_count': sum(item['qty'] for item in request.session.get('cart', []))
    })
