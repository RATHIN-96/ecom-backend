from django.contrib import admin
from .models import Product
from .models import Profile
from.models import Category
from.models import Cart
from.models import CartItem
from.models import Wishlist
from.models import Order
from.models import OrderItem

# Register your models here.




admin.site.register(Product)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(OrderItem)