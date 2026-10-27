from .models import Order

def cart_context(request):
 
    cart_items_count = 0
    cart_total = 0
    cart_items = []

    if request.user.is_authenticated:
        try:
          
            order = Order.objects.get(user=request.user, is_completed=False)
            cart_items = order.orderitem_set.all()
            
   
            cart_items_count = sum(item.quantity for item in cart_items)
          
            cart_total = sum(item.product.price * item.quantity for item in cart_items)
            
        except Order.DoesNotExist:
            pass 

    return {
        'cart_items_count': cart_items_count,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }