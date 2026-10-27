from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Product, ContactMessage, Category, Order, OrderItem

def home(request):
    featured_products = Product.objects.filter(is_active=True)[:8]
    context = {'featured_products': featured_products}
    return render(request, 'myapp/D.Mitra.html', context)

def contact(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            message=request.POST.get('message')
        )
        return render(request, 'myapp/Contact.html', {'success': True})
        
    return render(request, 'myapp/Contact.html')

def about(request):
    return render(request, 'myapp/About.html')

def products(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
   
    category_slug = request.GET.get('category')
    max_price = request.GET.get('max_price') 
    
    active_category = None

    if category_slug:
        active_category = Category.objects.get(slug=category_slug)
        products = products.filter(category=active_category)

    if max_price:
        try:
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass 
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'active_category': active_category,
        'current_max_price': max_price, 
    }
    
    return render(request, 'myapp/products.html', context)

def product_card(request, id):
    product = get_object_or_404(Product, id=id)
    context = {'product': product}
    return render(request, 'myapp/product-card.html', context)

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        subscribe = request.POST.get('subscribe') == 'yes' 

        if User.objects.filter(email=email).exists():
            context = {'error': 'An account with this email already exists.'}
            return render(request, 'myapp/Signin.html', context)

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        UserProfile.objects.create(user=user, newsletter_subscribed=subscribe)

        login(request, user)
        return redirect('home')

    return render(request, 'myapp/Signin.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = None
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            context = {'error': 'Invalid email or password. Please try again.'}
            return render(request, 'myapp/Login.html', context)
            
    return render(request, 'myapp/Login.html')

@login_required(login_url='login')
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    
    if request.method == 'POST':
        try:
            quantity_requested = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity_requested = 1
            
        if quantity_requested <= 0:
            messages.error(request, "Quantity must be at least 1.")
            return redirect(request.META.get('HTTP_REFERER', 'products'))

        if not hasattr(product, 'stock_record') or not product.stock_record.in_stock:
            messages.error(request, "Sorry, this item is currently out of stock.")
            return redirect(request.META.get('HTTP_REFERER', 'products'))
            
        available_stock = product.stock_record.quantity
        order, created = Order.objects.get_or_create(user=request.user, is_completed=False)
        order_item, item_created = OrderItem.objects.get_or_create(order=order, product=product)
        
        if item_created:
            new_total_quantity = quantity_requested
        else:
            new_total_quantity = order_item.quantity + quantity_requested
            
        if new_total_quantity > available_stock:
            order_item.quantity = available_stock
            order_item.save()
            messages.warning(request, f"We only have {available_stock} in stock! We adjusted your cart to the maximum available.")
        else:
            order_item.quantity = new_total_quantity
            order_item.save()
            messages.success(request, f"Added {quantity_requested} x {product.name} to your cart!")
            
    return redirect(request.META.get('HTTP_REFERER', 'products'))

def logout_user(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def checkout(request):
    order = get_object_or_404(Order, user=request.user, is_completed=False)
    items = order.orderitem_set.all()

    if request.method == 'POST':
        for item in items:
            stock = getattr(item.product, 'stock_record', None)
            
            if not stock:
                messages.error(request, f"Sorry, {item.product.name} is no longer available.")
                return redirect('checkout')

            if stock.quantity < item.quantity:
                messages.error(request, f"We only have {stock.quantity} unit(s) of {item.product.name} left. Please update your cart.")
                return redirect('checkout')

        for item in items:
            stock = item.product.stock_record
            stock.quantity -= item.quantity
            
            if stock.quantity <= 0:
                stock.quantity = 0
                
            stock.save()

        order.is_completed = True
        order.shipped = False
        order.delivered = False
        order.save()

        messages.success(request, "Order placed successfully! Thank you for shopping at D. Mitra.")
        return redirect('profile')

    context = {
        'order': order,
        'items': items,
        'cart_total': order.get_cart_total if hasattr(order, 'get_cart_total') else 0
    }
    return render(request, 'myapp/Checkout.html', context)

@login_required(login_url='login')
def profile(request):
    orders = Order.objects.filter(user=request.user, is_completed=True).order_by('-id')
    context = {'orders': orders}
    return render(request, 'myapp/Profile.html', context)

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    item_to_remove = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__is_completed=False)
    product_name = item_to_remove.product.name
    item_to_remove.delete()
    messages.success(request, f"{product_name} was removed from your cart.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))