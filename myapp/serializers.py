from rest_framework import serializers
from .models import Product
from .models import Stock


class ProductSerializer(serializers.ModelSerializer):
    in_stock = serializers.SerializerMethodField()
    stock_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "name",
            "description",
            "price",
            "image",
            "capacity",
            "power",
            "size",
            "available_colors",
            "is_active",
            "stock_quantity",
            "in_stock",
        ]

    def get_in_stock(self, obj):
        if hasattr(obj, "stock_record"):
            return obj.stock_record.in_stock
        return False

    def get_stock_quantity(self, obj):
        if hasattr(obj, "stock_record"):
            return obj.stock_record.quantity
        return 0
    
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"