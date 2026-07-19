from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.




class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Size(models.Model):

    name = models.CharField(
        max_length=20,
        unique=True
    )

    def __str__(self):

        return self.name  


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=200,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    sizes = models.ManyToManyField(Size,blank=True)
    has_size = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.user.username
    
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    size = models.ForeignKey(
        Size,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.product.name
    

class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    

class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    )

    REFUND_STATUS = (
        ('Not Applicable', 'Not Applicable'),
        ('Pending', 'Pending'),
        ('Refund Initiated', 'Refund Initiated'),
        ('Refunded', 'Refunded'),
        ('Rejected', 'Rejected'),
    )

    refund_status = models.CharField(
    max_length=20,
    choices=REFUND_STATUS,
    default='Not Applicable'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    phone = models.CharField(max_length=15)

    address = models.TextField()

    state = models.CharField(max_length=100,blank=True)

    district = models.CharField(max_length=100,blank=True)

    postoffice = models.CharField(max_length=100,blank=True)

    pincode = models.CharField(max_length=6,blank=True)

    delivery_charge = models.DecimalField(max_digits=10,decimal_places=2,default=0)

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    payment_id = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    razorpay_order_id = models.CharField(
    max_length=200,
    blank=True,
    null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    size = models.ForeignKey(
        Size,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product.name
    

class Review(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    

    
