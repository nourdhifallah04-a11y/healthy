"""
Serializers pour l'app orders
"""
from rest_framework import serializers
from .models import CartItem, Order, OrderItem
from apps.nutrition.serializers import FoodSerializer

class CartItemSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)
    total_calories = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'user', 'food', 'quantity', 'total_calories',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'food', 'quantity', 'unit_price', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'status', 'status_display', 'total_price',
            'delivery_address', 'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
