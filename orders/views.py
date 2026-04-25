from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.core.paginator import Paginator
from reviews.models import Product, Order, OrderItem
from functools import wraps
from decimal import Decimal

# Helper to get statistics
def get_admin_stats():
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    # "Giao trong ngày" can be orders with status 'shipping'
    today_delivery = Order.objects.filter(status='shipping').count()
    
    # Format revenue (e.g., 45.2 M or just plain number)
    rev_str = f"{total_revenue / 1000000:.1f} M" if total_revenue >= 1000000 else f"{total_revenue:,.0f} đ"
    
    return {
        "total_orders": f"{total_orders:,}",
        "pending_revenue": rev_str,
        "today_delivery": str(today_delivery),
    }

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden("Bạn không có quyền truy cập trang này.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@admin_required
def admin_dashboard(request):
    return render(request, "admin/dashboard.html", {
        "stats": get_admin_stats(),
        "is_admin_page": True
    })

@admin_required
def admin_orders(request):
    status = request.GET.get("status", "all")
    q = request.GET.get("q", "")
    page_number = request.GET.get("page", 1)
    sort = request.GET.get("sort", "desc") # Default sorting
    
    order_by = "-id" if sort == "desc" else "id"
    orders_qs = Order.objects.all().order_by(order_by)
    
    if status != "all":
        orders_qs = orders_qs.filter(status=status)
    
    if q:
        q_clean = q.lower()
        if q_clean.startswith('hd'):
            q_clean = q_clean[2:] # Bỏ 'HD'
        elif q_clean.startswith('kh'):
            q_clean = q_clean[2:] # Bỏ 'KH'
        
        # Thử ép kiểu số nếu chuỗi sạch chỉ toàn số
        search_id = None
        if q_clean.lstrip('0').isdigit():
            search_id = q_clean.lstrip('0')
            if not search_id: search_id = "0" # Trường hợp search toàn số 0

        qs_filter = Q(user__username__icontains=q) | \
                    Q(user__first_name__icontains=q) | \
                    Q(user__last_name__icontains=q) | \
                    Q(user__profile__phone__icontains=q)
        
        if search_id:
            qs_filter |= Q(id__iexact=search_id)
            
        orders_qs = orders_qs.filter(qs_filter)
    
    paginator = Paginator(orders_qs, 10) # 10 orders per page
    orders = paginator.get_page(page_number)
        
    all_products = Product.objects.all()
    all_users = User.objects.all()
    
    return render(request, "admin/orders_management.html", {
        "orders": orders,
        "paginator": paginator,
        "stats": get_admin_stats(),
        "status": status,
        "q": q,
        "sort": sort,
        "products": all_products,
        "users": all_users,
        "status_choices": Order.STATUS_CHOICES,
        "is_admin_page": True
    })

@admin_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = []
    subtotal = 0
    for item in order.items.all():
        subtotal += int(item.price) * int(item.quantity)
        items.append({
            "product_name": item.product_name,
            "color": item.color,
            "size": item.size,
            "quantity": item.quantity,
            "price": float(item.price),
            "image": item.product.image_name if item.product else "sp1.png"
        })
        
    discount = float(getattr(order, 'discount_amount', 0))
    if discount == 0:
        discount = float(subtotal - float(order.total_amount))
        if discount < 0: discount = 0
        
    coupon_code = getattr(order, 'coupon_code', '')
    if discount > 0 and not coupon_code:
        coupon_code = "GIAM50K" if int(discount) == 50000 else "WELCOME10"
        
    try:
        phone = order.user.profile.phone
        address = order.user.profile.address
    except Exception:
        phone = ""
        address = ""
    
    # Determine discount_val for editing
    discount_val = "0"
    if coupon_code == "WELCOME10":
        discount_val = "10"
    elif coupon_code == "GIAM50K":
        discount_val = "50000"

    data = {
        "id": order.id,
        "username": order.user.username,
        "fullname": order.user.first_name,
        "phone": phone,
        "address": address,
        "created_at": order.created_at.strftime("%d/%m/%Y %H:%M"),
        "status": order.get_status_display(),
        "status_slug": order.status,
        "total_amount": float(order.total_amount),
        "subtotal": float(subtotal),
        "discount_amount": float(discount),
        "discount_val": discount_val,
        "coupon_code": coupon_code or "Không có",
        "items": items
    }
    return JsonResponse(data)

@admin_required
def admin_create_order(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        
        product_ids = request.POST.getlist("product_ids[]")
        quantities = request.POST.getlist("quantities[]")
        colors = request.POST.getlist("colors[]")
        sizes = request.POST.getlist("sizes[]")
        status = request.POST.get("status", "pending")
        
        user = None
        if phone:
            user = User.objects.filter(username=phone).first()
            if not user:
                user = User.objects.create_user(username=phone, password="defaultpassword123", first_name=fullname)
            else:
                user.first_name = fullname
                user.save()
            
            from reviews.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.address = address
            profile.save()
        else:
            user_id = request.POST.get("user_id")
            user = get_object_or_404(User, id=user_id) if user_id else get_object_or_404(User, id=1)

        if not product_ids:
            return JsonResponse({"success": False, "error": "Vui lòng chọn ít nhất 1 sản phẩm cho đơn hàng!"})

        try:
            total = Decimal('0')
            order_items_data = []
            for i, pid in enumerate(product_ids):
                qty = int(quantities[i]) if i < len(quantities) else 1
                col = colors[i] if i < len(colors) else "White"
                siz = sizes[i] if i < len(sizes) else "M"
                
                product = get_object_or_404(Product, id=pid)
                order_items_data.append({
                    'product': product,
                    'name': product.name,
                    'color': col,
                    'size': siz,
                    'qty': qty,
                    'price': product.price
                })
                total += product.price * qty
                
            discount_val = request.POST.get("discount", "0")
            discount_amount = Decimal('0')
            coupon_code = ""

            if discount_val == "10":
                coupon_code = "WELCOME10"
                discount_amount = total * Decimal('0.1')
                total = total - discount_amount
            elif discount_val.isdigit() and int(discount_val) >= 100:
                coupon_code = "GIAM50K"
                discount_amount = Decimal(discount_val)
                total = total - discount_amount

            if total < 0:
                total = 0
                
            order = Order.objects.create(
                user=user, 
                status=status, 
                total_amount=total,
                coupon_code=coupon_code,
                discount_amount=discount_amount
            )
            
            for item in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['name'],
                    color=item['color'],
                    size=item['size'],
                    quantity=item['qty'],
                    price=item['price']
                )
                # Deduct stock
                item['product'].stock -= item['qty']
                item['product'].save()
                
            messages.success(request, f"Tạo đơn hàng HD{order.id:08d} thành công!")
            return JsonResponse({"success": True, "order_id": order.id, "name": fullname})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False})

@admin_required
def admin_edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        fullname = request.POST.get("fullname", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        
        product_ids = request.POST.getlist("product_ids[]")
        quantities = request.POST.getlist("quantities[]")
        colors = request.POST.getlist("colors[]")
        sizes = request.POST.getlist("sizes[]")
        status = request.POST.get("status", order.status)
        
        if not product_ids:
            return JsonResponse({"success": False, "error": "Đơn hàng phải có ít nhất 1 sản phẩm!"})

        try:
            # Update user/profile
            order.user.first_name = fullname
            order.user.save()
            from reviews.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=order.user)
            profile.phone = phone
            profile.address = address
            profile.save()

            # Process items (Clear and re-create)
            old_items = list(order.items.all())
            for item in old_items:
                if item.product:
                    item.product.stock += item.quantity
                    item.product.save()
            
            order.items.all().delete()
            
            total = Decimal('0')
            for i, pid in enumerate(product_ids):
                qty = int(quantities[i]) if i < len(quantities) else 1
                col = colors[i] if i < len(colors) else "White"
                siz = sizes[i] if i < len(sizes) else "M"
                
                product = get_object_or_404(Product, id=pid)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    color=col,
                    size=siz,
                    quantity=qty,
                    price=product.price
                )
                total += product.price * qty
                
                # Deduct new stock
                product.stock -= qty
                product.save()
                
            discount_val = request.POST.get("discount", "0")
            discount_amount = Decimal('0')
            coupon_code = ""

            if discount_val == "10":
                coupon_code = "WELCOME10"
                discount_amount = total * Decimal('0.1')
                total = total - discount_amount
            elif discount_val.isdigit() and int(discount_val) >= 100:
                coupon_code = "GIAM50K"
                discount_amount = Decimal(discount_val)
                total = total - discount_amount

            if total < 0: total = 0
            
            order.status = status
            order.total_amount = total
            order.coupon_code = coupon_code
            order.discount_amount = discount_amount
            order.save()
            
            messages.success(request, f"Cập nhật đơn hàng HD{order.id:08d} thành công!")
            return JsonResponse({"success": True, "name": fullname})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False})

@admin_required
def admin_delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_id_copy = order.id
    order.delete()
    messages.success(request, f"Xóa đơn hàng HD{order_id_copy:08d} thành công!")
    return redirect('admin_orders')

@admin_required
def admin_update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        status = request.POST.get("status")
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if status in valid_statuses:
            order.status = status
            order.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

@admin_required
def get_customer_info(request):
    phone = request.GET.get('phone', '').strip()
    name = request.GET.get('name', '').strip()
    user = None
    if phone:
        user = User.objects.filter(username=phone).first()
    elif name:
        user = User.objects.filter(first_name__icontains=name).first()
    
    if user:
        try:
            profile = user.profile
            return JsonResponse({
                "success": True,
                "fullname": user.first_name,
                "phone": profile.phone or user.username,
                "address": profile.address or ""
            })
        except Exception:
            pass
    return JsonResponse({"success": False})
