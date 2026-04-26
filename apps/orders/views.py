"""
Vues pour l'app orders
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CartItem, Order, OrderItem
from .serializers import CartItemSerializer, OrderSerializer
from apps.nutrition.models import Food

class CartViewSet(viewsets.ModelViewSet):
    """ViewSet pour le panier"""
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé du panier"""
        cart_items = CartItem.objects.filter(user=request.user)
        total_calories = sum(item.total_calories for item in cart_items)
        
        return Response({
            'items_count': cart_items.count(),
            'total_calories': total_calories,
        })
    
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Valider le panier et créer une commande"""
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = Order.objects.create(
            user=request.user,
            total_price=0,  # Calculer le prix total
            delivery_address=request.data.get('delivery_address', ''),
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                food=item.food,
                quantity=item.quantity,
                unit_price=0,  # Définir le prix
            )
        
        cart_items.delete()
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les commandes"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
