from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Product, Category, Order
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer

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
        
        # Check stock for each product
        for item in items:
            p_id = item.get('product_id')
            if not p_id:
                return Response(
                    {"message": "Mỗi sản phẩm trong đơn hàng phải có product_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                product = Product.objects.get(id=p_id)
                if product.stock <= 0:
                    return Response(
                        {"message": f"Sản phẩm '{product.name}' đã hết hàng"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (Product.DoesNotExist, ValueError):
                return Response(
                    {"message": f"Sản phẩm với ID {p_id} không tồn tại"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
