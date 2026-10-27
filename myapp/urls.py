from django.urls import path
from . import views
from .api_views import ProductCreateAPIView
from .api_views import ProductAPIView
from .api_views import StockUpdateAPIView
from .api_views import UpdateStockAPIView


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('products/', views.products, name='products'),
    path('product/<int:id>/', views.product_card, name='product_card'),
    path('remove-item/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('api/products/add/', ProductCreateAPIView.as_view(), name='product-add'),
    path("api/products/", ProductAPIView.as_view(), name="products-api"),
    path("api/products/<int:product_id>/stock/",UpdateStockAPIView.as_view(),name="update-stock",
    ),
]

urlpatterns += [
    path('api/stock/<int:pk>/',StockUpdateAPIView.as_view(),name='stock-update'),   
]