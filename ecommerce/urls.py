"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from product import views
from product.views import LoginAPIView
from product.views import *
from product.views import UserRegistrationView,UserProfileUpdateView
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static





urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('products/', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('profile/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('change-password/', views.ChangePasswordAPIView.as_view()),
    path('login/', LoginAPIView.as_view(), name='login'),

    path('categories/', CategoryList.as_view()),
    path('categories/<int:pk>/',CategoryDetail.as_view()),
    path('cart/', CartList.as_view()),
    path('cart-items/', CartItemList.as_view()),
    path('cart-items/<int:pk>/', CartItemDetail.as_view()),
    path('wishlist/', WishlistList.as_view()),
    path('wishlist/<int:pk>/', WishlistDetail.as_view()),
    path('orders/', OrderList.as_view()),
    path('orders/<int:pk>/', OrderDetail.as_view()),
    path('place-order/', PlaceOrderAPIView.as_view()),
    path("buy-now-order/", BuyNowOrderAPIView.as_view()),
    path("buy-now-create-payment/", BuyNowCreatePaymentAPIView.as_view()),
    path("buy-now-verify-payment/", BuyNowVerifyPaymentAPIView.as_view()),
    path('reviews/', views.ReviewList.as_view()),
    path('reviews/<int:pk>/', views.ReviewDetail.as_view()),
    path("create-payment/", CreatePaymentAPIView.as_view()),
    path("verify-payment/",VerifyPaymentAPIView.as_view()),
    path("invoice/<int:pk>/", DownloadInvoiceAPIView.as_view()),
    path('cancel-order/<int:pk>/',CancelOrderAPIView.as_view()),
    path('users/', UserListAPIView.as_view()),
    path('users/<int:pk>/toggle-status/',ToggleUserStatusAPIView.as_view()),
    path('admin-dashboard/',AdminDashboardAPIView.as_view()),
    path("sizes/", SizeList.as_view()),
    path("check-pincode/<str:pincode>/",CheckPincodeAPIView.as_view()),
    
    


]

    




from django.conf import settings
from django.conf.urls.static import static



# urlpatterns += static(
#     settings.MEDIA_URL,
#     document_root=settings.MEDIA_ROOT
# )
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)