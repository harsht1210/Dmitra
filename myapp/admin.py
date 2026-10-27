from django.contrib import admin, messages
from django.db.models import Sum
from .models import (
    UserProfile,
    Category,
    Product,
    Order,
    OrderItem,
    ContactMessage,
    Stock,
    Payment,
    Delivery
)

# Basic Models
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    pass


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


# Stock
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'last_updated', 'in_stock')
    search_fields = ('product__name',)
    list_editable = ('quantity',)


# Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'order',
        'payment_method',
        'amount_paid',
        'status',
        'created_at'
    )
    list_filter = ('status', 'payment_method')
    search_fields = ('transaction_id', 'order__id')
    list_editable = ('status',)


# Delivery
@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'status',
        'tracking_number',
        'courier_partner'
    )
    list_filter = ('status',)
    search_fields = ('tracking_number', 'order__id')
    list_editable = ('status',)


# Inlines
class PaymentInline(admin.StackedInline):
    model = Payment
    can_delete = False
    extra = 0


class DeliveryInline(admin.StackedInline):
    model = Delivery
    can_delete = False
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity')
    can_delete = False
    extra = 0


# Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'get_payment_status',
        'get_delivery_status',
        'get_order_revenue',
        'is_approved_by_admin'
    )
    list_filter = ('is_approved_by_admin', 'is_completed')
    list_editable = ('is_approved_by_admin',)
    inlines = [PaymentInline, DeliveryInline, OrderItemInline]

    def get_payment_status(self, obj):
        payment = Payment.objects.filter(order=obj).first()
        return payment.status if payment else 'No Payment'
    get_payment_status.short_description = 'Payment Status'

    def get_delivery_status(self, obj):
        delivery = Delivery.objects.filter(order=obj).first()
        return delivery.status if delivery else 'No Delivery'
    get_delivery_status.short_description = 'Delivery Status'

    def get_order_revenue(self, obj):
        payment = Payment.objects.filter(order=obj).first()
        if payment and payment.amount_paid:
            return f"₹{payment.amount_paid}"
        return "₹0.00"
    get_order_revenue.short_description = 'Order Revenue'

    def changelist_view(self, request, extra_context=None):
        total_income = Payment.objects.filter(
            status='Completed'
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0.00

        messages.info(request, f"Total Income: ₹{total_income}")
        return super().changelist_view(request, extra_context=extra_context)