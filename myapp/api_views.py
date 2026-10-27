from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .models import Stock
from .serializers import ProductSerializer
from .serializers import StockSerializer


class ProductCreateAPIView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class StockUpdateAPIView(generics.UpdateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

class UpdateStockAPIView(APIView):

    def put(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            stock = product.stock_record

            quantity = request.data.get("quantity")

            if quantity is None:
                return Response(
                    {"error": "Quantity is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            stock.quantity = int(quantity)
            stock.save()

            return Response({
                "message": "Stock updated successfully",
                "product": product.name,
                "quantity": stock.quantity,
                "in_stock": stock.in_stock
            })

        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )