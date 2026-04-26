"""
Admin pour l'app orders
"""
from django.contrib import admin
from .models import CartItem, Order, OrderItem, Commande, LigneCommande


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


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id_commande', 'client', 'statut', 'total', 'date']
    list_filter = ['statut', 'date']
    search_fields = ['client__utilisateur__email', 'id_commande']
    fieldsets = (
        ('Informations', {'fields': ('client', 'date')}),
        ('Statut', {'fields': ('statut', 'total')}),
        ('Livraison', {'fields': ('adresse_livraison', 'notes')}),
    )
    readonly_fields = ['date']


@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ['commande', 'get_item_name', 'get_item_type', 'quantite', 'prix_unitaire']
    list_filter = ['commande__date']
    search_fields = ['commande__id_commande', 'plat__nom', 'menu__nom']

