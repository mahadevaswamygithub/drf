from rest_framework.routers import DefaultRouter
from api.views import OrderViewSet

api_router = DefaultRouter()
api_router.register('orders', OrderViewSet)