from django.urls import path, include
from . import views

from api.routers import api_router

urlpatterns = [
    # path('products/', views.product_list),
    path('products/', views.ProductListCreateAPIView.as_view()),
    # path('products/<int:pk>/', views.product_detail), 
    # path('products/<int:pk>/', views.ProductDetailAPIView.as_view()), 
    path('products/<int:product_id>/', views.ProductRetrieveUpdateDestroyAPIView.as_view()), 
    # path('orders/', views.order_list),  
    # path('products/info/', views.product_info),
    path('products/info/', views.ProductInfoAPIView.as_view()),
    # path('user-order/',views.UserOrderListAPIView.as_view(), name = 'user-orders'),
    # path('orders/', views.OrderListAPIView.as_view()),
]

urlpatterns += api_router.urls


