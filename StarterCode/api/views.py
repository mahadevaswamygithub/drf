from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from api.serializers import (ProductSerializer,
                            OrderSerializer, 
                            ProductInfoSerializer, 
                            OrderCreateUpdateSerializer)
from api.models import Product, Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Max, Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework import viewsets

from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny
)
from rest_framework.views import APIView
from api.filters import ProductFilter, InStockFilterBackend, OrderFilter


# django views
# def product_list(request):
#     products = Product.objects.all()

#     serializer = ProductSerializer(products, many=True)

#     return JsonResponse({
#         'data': serializer.data
#     })

# Function Based Views:

# @api_view(['GET'])
# def product_list(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data)

# @api_view(['GET'])
# def product_detail(request, pk):
#     product = get_object_or_404(Product, pk=pk)
#     serializer = ProductSerializer(product)
#     return Response(serializer.data)

# @api_view(['GET'])
# def order_list(request):
#     # orders = Order.objects.all()
#     # orders = Order.objects.prefetch_related('items', 'items__product').all()
#     orders = Order.objects.prefetch_related('items__product').all() # No need to prefetch the items its automatically fetches items while fetcing items__products
#     serializer = OrderSerializer(orders, many=True)
#     return Response(serializer.data)

# @api_view(['GET'])
# def product_info(request):
#     products = Product.objects.all()
#     serializer = ProductInfoSerializer({
#         'products':products,
#         'count': len(products),
#         'max_price': products.aggregate(max_price=Max('price'))['max_price'],
#         'min_price': products.aggregate(min_price=Min('price'))['min_price'],
#     })
#     return Response(serializer.data)

    

# class based views
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # filterset_fields = ('name', 'price')
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend,
                        filters.SearchFilter,
                        filters.OrderingFilter,
                        InStockFilterBackend]
    search_fields = ['=name', 'description']
    ordering_fields = ['price','name']
    # pagination_class = PageNumberPagination
    # pagination_class.page_size=2
    # pagination_class.page_query_param='pagenum'
    # pagination_class.page_size_query_param='size'
    # pagination_class.max_page_size=5
    pagination_class = LimitOffsetPagination



    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
             self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)
    
class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products':products,
            'count': len(products),
            'max_price': products.aggregate(max_price=Max('price'))['max_price'],
            'min_price': products.aggregate(min_price=Min('price'))['min_price'],
        })
        return Response(serializer.data)

class ProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'
    

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ['PUT',"DELETE", "PATCH"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(user= self.request.user)

    def get_queryset(self):
        qs =  super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs
    
    def get_serializer_class(self):
        # Can also check if POST: if self.request.method == 'POST'
        if self.action == 'create' or 'update':
            return OrderCreateUpdateSerializer
        return super().get_serializer_class()


    # @action(
    #         detail=False, 
    #         methods=['GET'],
    #         url_path='user-orders',
    #         permission_classes = [IsAuthenticated]
    #     )
    # def user_orders(self, request, *args, **kwargs):
    #     orders = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(orders, many=True)
    #     return Response(serializer.data)