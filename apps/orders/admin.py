"""
Admin pour l'app orders
"""
from django.contrib import admin
from .models import CartItem, Order, OrderItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'food', 'quantity', 'created_at']
    search_fields = ['user__username', 'food__name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'food', 'quantity', 'unit_price']
    search_fields = ['order__id', 'food__name']
