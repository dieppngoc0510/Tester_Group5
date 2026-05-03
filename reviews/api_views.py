from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Product, Category, Order, OrderItem, UserProfile
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer
import re


@method_decorator(csrf_exempt, name='dispatch')
class UserProfileAPI(APIView):
    """
    GET  /api/user/profile/ – Lấy thông tin cá nhân (session auth)
    PUT  /api/user/profile/ – Cập nhật thông tin cá nhân
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data = {
            "fullname": user.first_name,
            "email": user.email,
            "phone": profile.phone or "",
            "address": profile.address or "",
            "gender": profile.gender or "",
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data = request.data

        fullname = data.get("fullname", user.first_name)
        phone    = data.get("phone", profile.phone or "")
        address  = data.get("address", profile.address or "")

        # Validate phone
        if phone and not re.fullmatch(r'\d{10}', str(phone)):
            return Response(
                {"phone": "Số điện thoại không hợp lệ! Phải bao gồm đúng 10 chữ số."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.first_name = fullname
        user.save()

        profile.phone   = phone
        profile.address = address
        profile.save()

        return Response({
            "message": "Cập nhật thành công",
            "fullname": user.first_name,
            "phone": profile.phone,
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordAPI(APIView):
    """
    PUT /api/user/change-password/ – Đổi mật khẩu (session auth)
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')

        if not old_password or not new_password:
            return Response(
                {'error': 'Vui lòng nhập đầy đủ mật khẩu cũ và mật khẩu mới.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.check_password(old_password):
            return Response(
                {'old_password': 'Mật khẩu hiện tại không đúng.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 8:
            return Response(
                {'new_password': 'Mật khẩu mới phải có ít nhất 8 ký tự.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(new_password)
        request.user.save()

        return Response(
            {'message': 'Cập nhật mật khẩu thành công'},
            status=status.HTTP_200_OK
        )

class Login(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not User.objects.filter(username=username).exists():
            return Response({"message": "Tài khoản không tồn tại"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Credentials are incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

class Logout(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            pass
        return Response({"message": "Đăng xuất thành công"}, status=status.HTTP_200_OK)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.all()
        search_keyword = self.request.query_params.get('search', '').strip()
        category_id = self.request.query_params.get('category', '').strip()

        if search_keyword:
            queryset = queryset.filter(name__icontains=search_keyword)

        if category_id:
            if category_id.isdigit():
                queryset = queryset.filter(categories__id=int(category_id))
            else:
                queryset = queryset.none()

        return queryset.distinct()

    def retrieve(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        try:
            product = Product.objects.get(pk=product_id)
        except (Product.DoesNotExist, ValueError):
            return Response(
                {'message': 'Sản phẩm không tồn tại'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        total_amount = request.data.get('total_amount')
        address = request.data.get('address')
        items = request.data.get('items')

        if not total_amount or not address:
            return Response(
                {"message": "Thiếu dữ liệu bắt buộc: total_amount và address"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not items or len(items) == 0:
            return Response(
                {"message": "Đơn hàng phải có ít nhất 1 sản phẩm"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check stock and existence for each product
        for item in items:
            p_id = item.get('product_id')
            qty = int(item.get('quantity', 1))
            
            if not p_id:
                return Response(
                    {"message": "Mỗi sản phẩm trong đơn hàng phải có product_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                product = Product.objects.get(id=p_id)
                if product.stock < qty:
                    return Response(
                        {"message": f"Sản phẩm '{product.name}' không đủ tồn kho (còn {product.stock})"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (Product.DoesNotExist, ValueError):
                return Response(
                    {"message": f"Sản phẩm với ID {p_id} không tồn tại"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Lấy dữ liệu từ request
        items_data = self.request.data.get('items', [])
        address = self.request.data.get('address')
        
        # Cập nhật địa chỉ vào Profile của user (giống logic bên admin)
        if address:
            from .models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=self.request.user)
            profile.address = address
            profile.save()

        # Lưu đơn hàng với trạng thái mặc định là pending
        order = serializer.save(user=self.request.user, status='pending')
        
        # Tạo các chi tiết đơn hàng (OrderItem) và trừ tồn kho
        for item_data in items_data:
            p_id = item_data.get('product_id')
            qty = int(item_data.get('quantity', 1))
            product = Product.objects.get(id=p_id)
            
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                quantity=qty,
                price=product.price,
                color=item_data.get('color', 'Mặc định'),
                size=item_data.get('size', 'L')
            )
            
            # Trừ tồn kho
            product.stock -= qty
            product.save()
