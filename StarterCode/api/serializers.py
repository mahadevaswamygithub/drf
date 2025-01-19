from rest_framework import serializers
from .models import Product, Order, OrderItem
from django.db import transaction

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'stock'
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Price must br greater then 0."
            )
        return value
    
class OrderItemSerializer(serializers.ModelSerializer):

    # product = ProductSerializer()  # To get the all details about the product

    product_name = serializers.CharField(source='product.name') # to get only the name of the product
    product_price = serializers.DecimalField(source='product.price',
                                          max_digits=10,
                                          decimal_places=2
                                          ) # to get only the price of the product

    class Meta:
        model = OrderItem
        fields = ('product_name', 'product_price', 'product', 'quantity', 'item_subtotal')


class OrderCreateUpdateSerializer(serializers.ModelSerializer):

    class OrderItemCreateUpdateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields =('product', 'quantity')

    items = OrderItemCreateUpdateSerializer(many=True, required=False)
    total_price = serializers.SerializerMethodField(method_name='total')

    def create(self, validated_data):
        orderitem_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item in orderitem_data:
            OrderItem.objects.create(order=order, **item)

        return order
    
    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items')
        with transaction.atomic():
            instance = super().update(instance=instance, validated_data=validated_data)
            if orderitem_data is not None:
                #clear existing iteams (optional)
                instance.items.all().delete()

                #Recreate
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item)

        return instance

    def total(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        model = Order
        fields = ("created_at", "user", "status", 'items', 'total_price')
        extra_kwargs = {
            'user':{'read_only':True}
        }





class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    order_id = serializers.UUIDField(read_only=True)

    # total_price = serializers.SerializerMethodField(method_name='total')
    # def total(self, obj):
    #     order_items = obj.items.all()
    #     return sum(order_item.item_subtotal for order_item in order_items)


    def get_total_price(self, obj):

        order_items = obj.items.all()

        return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        model = Order
        fields = ('order_id', "created_at", "user", "status", 'items', 'total_price')
        

# Generic Serializers
class ProductInfoSerializer(serializers.Serializer):
    # Get all Products, count of products, Max price
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()
    min_price = serializers.FloatField()