from rest_framework import serializers
from .models import Product
from django.contrib.auth.models import User
from django.db.models import Avg

from .models import *

from .models import Profile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

from django.db.models import Avg

class ProductSerializer(serializers.ModelSerializer):

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    category = CategorySerializer(read_only=True)

    average_rating = serializers.SerializerMethodField()

    review_count = serializers.SerializerMethodField()

    discounted_price = serializers.SerializerMethodField()

    class Meta:

        model = Product

        fields = [
            'id',
            'name',
            'price',
            'description',
            'image',
            'category',
            'category_id',
            'average_rating',
            'review_count',
            'discount_percentage',
            'discounted_price',
            ]

    def get_average_rating(self, obj):

        avg = obj.reviews.aggregate(
            Avg('rating')
        )['rating__avg']

        if avg:
            return round(avg, 1)

        return 0

    def get_review_count(self, obj):

        return obj.reviews.count()
    
    def get_discounted_price(self, obj):

        if obj.discount_percentage > 0:

            discount = (obj.price * obj.discount_percentage) / 100

            return round(obj.price - discount, 2)

        return obj.price



class UserSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(
        source='profile.phone',
        required=False
    )

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'phone',
            'is_staff',
            'is_active'
        )

        extra_kwargs = {
            'password': {
                'write_only': True,
                'allow_null': True,
                'required': False,
            }
        }

    def create(self, validated_data):

        profile_data = validated_data.pop('profile', {})

        phone = profile_data.get('phone')

        user = User.objects.create_user(**validated_data)

        Profile.objects.create(
            user=user,
            phone=phone
        )

        return user

    def update(self, instance, validated_data):

        profile_data = validated_data.pop('profile', {})

        phone = profile_data.get('phone')

        instance.first_name = validated_data.get(
            'first_name',
            instance.first_name
        )

        instance.last_name = validated_data.get(
            'last_name',
            instance.last_name
        )

        instance.email = validated_data.get(
            'email',
            instance.email
        )

        instance.save()

        profile, _ = Profile.objects.get_or_create(
            user=instance
        )

        if phone is not None:

            profile.phone = phone

            profile.save()

        return instance



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'




class CartItemSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'product_id']

class OrderItemSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True, read_only=True)

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'name',
            'phone',
            'address',
            'total_price',
            'status',
            'payment_status',
            'refund_status',
            'payment_id',
            'created_at',
            'items'
        ]


class ReviewSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.username')
    is_owner = serializers.SerializerMethodField()


    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'product',
            'rating',
            'comment',
            'created_at',
            'is_owner'
        ]
        read_only_fields = ['user', 'created_at']

    def get_is_owner(self, obj):
        request = self.context.get('request')

        if request:
             return obj.user == request.user

        return False
    