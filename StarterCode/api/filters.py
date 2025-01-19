import django_filters
from api.models import Product, Order
from rest_framework import filters

class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        # fields = ('name', 'price')
        fields = {         
            "name": ["exact", "icontains"],  
            "price": ["exact", "lt", "gt", "range"]
        }



class InStockFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(stock__gt=0)
    

class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name='created_at__date')

    class Meta:
        model = Order
        fields = {
            'status': ['exact'],
            'created_at':  ["exact", "lt", "gt", "range"]
        }