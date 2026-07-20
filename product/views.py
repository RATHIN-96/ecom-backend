from django.shortcuts import render

from rest_framework import generics,permissions, status
from .models import Product
from .serializers import ProductSerializer

from django.contrib.auth.models import User  
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny

from .models import *
from .serializers import *
import os
from django.db.models import Sum

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated

from django.db.models import Q

from rest_framework.views import APIView  
from rest_framework.response import Response  
from rest_framework import status
from django.db.models import Avg

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import razorpay
from django.conf import settings

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from decimal import Decimal
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from rest_framework.parsers import MultiPartParser, FormParser






client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)

class LoginAPIView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        token, created = Token.objects.get_or_create(user=user)

        return Response({

            "token": token.key,

            "id": user.id,

            "username": user.username,

            "first_name": user.first_name,

            "email": user.email,

            "is_staff": user.is_staff

        })

def home(request):
    return HttpResponse("Welcome to My page")

class ProductDetailAPIView(generics.RetrieveAPIView):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer

    permission_classes = [AllowAny]


class ProductList(generics.ListCreateAPIView):

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):

        queryset = Product.objects.all()

        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        price = self.request.GET.get('price')
        sort = self.request.GET.get('sort')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        if category:
            queryset = queryset.filter(category_id=category)

        if price == "1":
            queryset = queryset.filter(price__lt=10000)

        elif price == "2":
            queryset = queryset.filter(
                price__gte=10000,
                price__lte=50000
            )

        elif price == "3":
            queryset = queryset.filter(price__gt=50000)

        if sort == "low":
            queryset = queryset.order_by("price")

        elif sort == "high":
            queryset = queryset.order_by("-price")

        elif sort == "new":
            queryset = queryset.order_by("-id")

        return queryset
from rest_framework import permissions

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = Product.objects.all()

    serializer_class = ProductSerializer

    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):

        if self.request.method == "GET":
            return [permissions.AllowAny()]

        return [permissions.IsAdminUser()]


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,) 




class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        
        return self.request.user


class UserListAPIView(generics.ListAPIView):

    queryset = User.objects.all().order_by('-id')

    serializer_class = UserSerializer

    permission_classes = [permissions.AllowAny]


class ToggleUserStatusAPIView(APIView):

    permission_classes = [permissions.AllowAny]

    def patch(self, request, pk):

        try:

            user = User.objects.get(pk=pk)

            
            if request.user.is_authenticated and user == request.user:

                return Response(
                    {"error": "You cannot block your own account."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user.is_staff:

                return Response(
                    {"error": "Admin accounts cannot be blocked."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Toggle Active / Blocked
            user.is_active = not user.is_active

            user.save()

            return Response({

                "message": "User status updated successfully.",

                "is_active": user.is_active

            })

        except User.DoesNotExist:

            return Response(

                {"error": "User not found."},

                status=status.HTTP_404_NOT_FOUND

            )


class CategoryList(generics.ListCreateAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):

        if self.request.method == "GET":
            return [permissions.AllowAny()]

        return [IsAdminUser()]


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):

        if self.request.method == "GET":
            return [permissions.AllowAny()]

        return [IsAdminUser()]
    


class CartList(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [AllowAny]


class WishlistList(generics.ListCreateAPIView):

    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):

        product_id = request.data.get("product_id")

        if Wishlist.objects.filter(
            user=request.user,
            product_id=product_id
        ).exists():

            return Response(
                {
                    "message": "Product already exists in wishlist."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class WishlistDetail(generics.DestroyAPIView):

    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)



class OrderList(generics.ListCreateAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        print("User:", self.request.user)
        print("Is Staff:", self.request.user.is_staff)

        if self.request.user.is_staff:
            return Order.objects.all().order_by('-created_at')

        return Order.objects.filter(
            user=self.request.user
            ).order_by('-created_at')

    def perform_create(self, serializer):

        serializer.save(
            user=self.request.user
        )


class OrderDetail(generics.RetrieveUpdateAPIView):

    queryset = Order.objects.all()

    serializer_class = OrderSerializer

    permission_classes = [permissions.AllowAny]






class CartItemList(generics.ListCreateAPIView):

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return CartItem.objects.filter(
            cart__user=self.request.user
        )

    def perform_create(self, serializer):

        cart, created = Cart.objects.get_or_create(
            user=self.request.user
        )

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)
        size = serializer.validated_data.get("size", None)

        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            size=size
        ).first()

        if cart_item:

            cart_item.quantity += quantity
            cart_item.save()

        else:

            serializer.save(
                cart=cart
            )



class CartItemDetail(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        )



class PlaceOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        name = request.data.get("name")
        phone = request.data.get("phone")
        address = request.data.get("address")

        state = request.data.get("state")
        district = request.data.get("district")
        postoffice = request.data.get("postoffice")
        pincode = request.data.get("pincode")

        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():

            return Response(
                {"message": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------
        # Calculate Items Total
        # -------------------------

        items_total = Decimal("0.00")

        for item in cart_items:

            if item.product.discount_percentage > 0:

                discounted_price = item.product.price - (

                    item.product.price *
                    Decimal(item.product.discount_percentage) /
                    Decimal("100")

                )

            else:

                discounted_price = item.product.price

            items_total += discounted_price * item.quantity

        # -------------------------
        # Delivery Charge
        # -------------------------

        if items_total >= Decimal("999"):

            delivery_charge = Decimal("0.00")

        else:

            delivery_charge = Decimal("50.00")

        # -------------------------
        # Grand Total
        # -------------------------

        grand_total = items_total + delivery_charge

        # -------------------------
        # Create Order
        # -------------------------

        order = Order.objects.create(

            user=request.user,

            name=name,
            phone=phone,
            address=address,

            state=state,
            district=district,
            postoffice=postoffice,
            pincode=pincode,

            delivery_charge=delivery_charge,

            total_price=grand_total,

            status="Pending",

            payment_status="Pending"

        )

        # -------------------------
        # Order Items
        # -------------------------

        for item in cart_items:

            if item.product.discount_percentage > 0:

                discounted_price = item.product.price - (

                    item.product.price *
                    Decimal(item.product.discount_percentage) /
                    Decimal("100")

                )

            else:

                discounted_price = item.product.price

            OrderItem.objects.create(

                order=order,

                product=item.product,

                quantity=item.quantity,

                size=item.size,

                price=discounted_price

            )

        # -------------------------
        # Clear Cart
        # -------------------------

        cart_items.delete()

        return Response({

            "message": "COD Order Placed Successfully",

            "order_id": order.id,

            "items_total": items_total,

            "delivery_charge": delivery_charge,

            "grand_total": grand_total

        })
    
class BuyNowOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        size_id = request.data.get("size_id")

        name = request.data.get("name")
        phone = request.data.get("phone")
        address = request.data.get("address")

        state = request.data.get("state")
        district = request.data.get("district")
        postoffice = request.data.get("postoffice")
        pincode = request.data.get("pincode")

        try:

            product = Product.objects.get(id=product_id)

        except Product.DoesNotExist:

            return Response(
                {"message": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------
        # Size
        # -------------------------

        size = None

        if size_id:

            try:

                size = Size.objects.get(id=size_id)

            except Size.DoesNotExist:

                return Response(
                    {"message": "Invalid size"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # -------------------------
        # Discount Price
        # -------------------------

        if product.discount_percentage > 0:

            discounted_price = product.price - (

                product.price *
                Decimal(product.discount_percentage) /
                Decimal("100")

            )

        else:

            discounted_price = product.price

        # -------------------------
        # Items Total
        # -------------------------

        items_total = discounted_price * quantity

        # -------------------------
        # Delivery Charge
        # -------------------------

        if items_total >= Decimal("999"):

            delivery_charge = Decimal("0.00")

        else:

            delivery_charge = Decimal("50.00")

        # -------------------------
        # Grand Total
        # -------------------------

        grand_total = items_total + delivery_charge

        # -------------------------
        # Create Order
        # -------------------------

        order = Order.objects.create(

            user=request.user,

            name=name,
            phone=phone,
            address=address,

            state=state,
            district=district,
            postoffice=postoffice,
            pincode=pincode,

            delivery_charge=delivery_charge,

            total_price=grand_total,

            status="Pending",

            payment_status="Pending"

        )

        # -------------------------
        # Create Order Item
        # -------------------------

        OrderItem.objects.create(

            order=order,

            product=product,

            quantity=quantity,

            size=size,

            price=discounted_price

        )

        return Response({

            "message": "Buy Now Order Placed Successfully",

            "order_id": order.id,

            "items_total": items_total,

            "delivery_charge": delivery_charge,

            "grand_total": grand_total

        })
    
class CancelOrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:

            order = Order.objects.get(
                id=pk,
                user=request.user
            )

            # Cannot cancel after shipping
            if order.status in [
                "Shipped",
                "Out for Delivery",
                "Delivered",
                "Cancelled"
            ]:

                return Response(
                    {
                        "message": "This order cannot be cancelled."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            order.status = "Cancelled"

            # Refund Logic
            if order.payment_status == "Success":

                order.refund_status = "Pending"

            else:

                order.refund_status = "Not Applicable"

            order.save()

            return Response({

                "message": "Order Cancelled Successfully"

            })

        except Order.DoesNotExist:

            return Response({

                "message": "Order Not Found"

            }, status=status.HTTP_404_NOT_FOUND)  
        

class ChangePasswordAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):

            return Response(
                {"error": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            validate_password(new_password, user)
        

        except ValidationError as e:

            return Response(
                {"error": e.messages},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response({
            "message": "Password changed successfully"
        })
    

class ReviewList(generics.ListCreateAPIView):

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        product_id = self.request.GET.get('product')

        return Review.objects.filter(
            product_id=product_id
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)

        average = queryset.aggregate(
            Avg('rating')
        )['rating__avg']

        return Response({

            "average_rating": average or 0,

            "review_count": queryset.count(),

            "reviews": serializer.data

        })

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)

class ReviewDetail(generics.DestroyAPIView):

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Review.objects.filter(
            user=self.request.user
        )

class CreatePaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        name = request.data.get("name")
        phone = request.data.get("phone")
        address = request.data.get("address")

        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total = 0

        total = Decimal("0.00")

        for item in cart_items:

            if item.product.discount_percentage > 0:

                discounted_price = item.product.price - (
                    item.product.price *
                    Decimal(item.product.discount_percentage) /
                    Decimal("100")
                )

            else:

                discounted_price = item.product.price

        total += discounted_price * item.quantity

        # 1️⃣ Create Pending Order

        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address=address,
            total_price=total,
            status="Pending",
            payment_status="Pending"
        )

        # 2️⃣ Create Razorpay Order

        payment = client.order.create({
            "amount": int(total * 100),
            "currency": "INR",
            "payment_capture": 1
        })

        # 3️⃣ Save Razorpay Order ID

        order.razorpay_order_id = payment["id"]
        order.save()

        return Response({
            "order_id": payment["id"],
            "amount": payment["amount"],
            "currency": payment["currency"],
            "key": settings.RAZORPAY_KEY_ID
        })
    
class BuyNowCreatePaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        name = request.data.get("name")
        phone = request.data.get("phone")
        address = request.data.get("address")

        state = request.data.get("state")
        district = request.data.get("district")
        postoffice = request.data.get("postoffice")
        pincode = request.data.get("pincode")

        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        size_id = request.data.get("size_id")

        try:

            product = Product.objects.get(id=product_id)

        except Product.DoesNotExist:

            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------
        # Size
        # -------------------------

        size = None

        if size_id:

            try:

                size = Size.objects.get(id=size_id)

            except Size.DoesNotExist:

                return Response(
                    {"error": "Invalid size"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # -------------------------
        # Discount Price
        # -------------------------

        if product.discount_percentage > 0:

            discounted_price = product.price - (

                product.price *
                Decimal(product.discount_percentage) /
                Decimal("100")

            )

        else:

            discounted_price = product.price

        # -------------------------
        # Items Total
        # -------------------------

        items_total = discounted_price * quantity

        # -------------------------
        # Delivery Charge
        # -------------------------

        if items_total >= Decimal("999"):

            delivery_charge = Decimal("0.00")

        else:

            delivery_charge = Decimal("50.00")

        # -------------------------
        # Grand Total
        # -------------------------

        grand_total = items_total + delivery_charge

        # -------------------------
        # Create Pending Order
        # -------------------------

        order = Order.objects.create(

            user=request.user,

            name=name,
            phone=phone,
            address=address,

            state=state,
            district=district,
            postoffice=postoffice,
            pincode=pincode,

            delivery_charge=delivery_charge,

            total_price=grand_total,

            status="Pending",

            payment_status="Pending"

        )

        # -------------------------
        # Create Razorpay Order
        # -------------------------

        payment = client.order.create({

            "amount": int(grand_total * 100),

            "currency": "INR",

            "payment_capture": 1

        })

        # -------------------------
        # Save Razorpay Order ID
        # -------------------------

        order.razorpay_order_id = payment["id"]

        order.save()

        return Response({

            "order_id": payment["id"],

            "amount": payment["amount"],

            "currency": payment["currency"],

            "key": settings.RAZORPAY_KEY_ID,

            "items_total": items_total,

            "delivery_charge": delivery_charge,

            "grand_total": grand_total

        })
    
class VerifyPaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        try:

            # Verify Razorpay Signature
            client.utility.verify_payment_signature({

                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature

            })

            # Get Pending Order
            order = Order.objects.get(
                user=request.user,
                razorpay_order_id=razorpay_order_id,
                payment_status="Pending"
            )

            # Update Payment Details
            
            order.payment_id = razorpay_payment_id
            order.payment_status = "Success"
            order.status = "Paid"
            order.save()

            # Get User Cart
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)

            # Create Order Items
            for item in cart_items:

                if item.product.discount_percentage > 0:

                    discounted_price = item.product.price - (

                        item.product.price *
                        Decimal(item.product.discount_percentage) /
                        Decimal("100")

                    )

                else:

                    discounted_price = item.product.price

                OrderItem.objects.create(

                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=discounted_price

                )

            # Clear Cart
            cart_items.delete()

            return Response({

                "success": True,
                "message": "Payment Verified Successfully"

            })

        except Exception as e:

            return Response({

                "success": False,
                "message": str(e)

            }, status=status.HTTP_400_BAD_REQUEST)
        

class BuyNowVerifyPaymentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        try:

            client.utility.verify_payment_signature({

                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature

            })

            order = Order.objects.get(

                user=request.user,
                razorpay_order_id=razorpay_order_id,
                payment_status="Pending"

            )

            order.payment_id = razorpay_payment_id
            order.payment_status = "Success"
            order.status = "Paid"
            order.save()

            product_id = request.data.get("product_id")
            quantity = int(request.data.get("quantity", 1))
            size_id = request.data.get("size_id")

            try:

                product = Product.objects.get(id=product_id)

            except Product.DoesNotExist:

                return Response({

                    "success": False,
                    "message": "Product not found"

                }, status=status.HTTP_404_NOT_FOUND)

            size = None

            if size_id:

                try:

                    size = Size.objects.get(id=size_id)

                except Size.DoesNotExist:

                    return Response({

                        "success": False,
                        "message": "Invalid size"

                    }, status=status.HTTP_400_BAD_REQUEST)

            if product.discount_percentage > 0:

                discounted_price = product.price - (

                    product.price *
                    Decimal(product.discount_percentage) /
                    Decimal("100")

                )

            else:

                discounted_price = product.price

            OrderItem.objects.create(

                order=order,

                product=product,

                quantity=quantity,

                size=size,

                price=discounted_price

            )

            return Response({

                "success": True,

                "message": "Payment Verified Successfully"

            })

        except Exception as e:

            return Response({

                "success": False,

                "message": str(e)

            }, status=status.HTTP_400_BAD_REQUEST)


class SizeList(generics.ListCreateAPIView):

    queryset = Size.objects.all()

    serializer_class = SizeSerializer

    permission_classes = [AllowAny]
        

class DownloadInvoiceAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:

            # Admin can download any invoice

            if request.user.is_staff:

                order = Order.objects.get(id=pk)

                # Customer can download only their own invoice

            else:

                order = Order.objects.get(

                    id=pk,

                    user=request.user

                )

        except Order.DoesNotExist:

            return Response(

                {"message": "Order Not Found"},

                status=404

            )

        buffer = BytesIO()

        pdf = SimpleDocTemplate(
            buffer,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=20
        )

        styles = getSampleStyleSheet()

        elements = []

        logo_path = os.path.join(
            settings.BASE_DIR,
            "static",
            "logo.png"
        )

        if os.path.exists(logo_path):

            logo = Image(
            logo_path,
            width=170,
            height=70
        )

        logo.hAlign = "LEFT"

        elements.append(logo)

        elements.append(Spacer(1,10))

        # -----------------------------
        # Title
        # -----------------------------

        title_style = styles['Title']
        title_style.alignment = TA_CENTER
        title_style.textColor = colors.HexColor("#0d6efd")

        elements.append(
            Paragraph("<b>VELORA STORE</b>", title_style)
        )

        elements.append(
            Paragraph(
                "<para align='center'>E-Commerce Invoice</para>",
                styles['Heading2']
            )
        )

        elements.append(
            Paragraph(
                "<para align='center'>Thank you for shopping with us ❤️</para>",
                styles['Normal']
            )
        )

        elements.append(
            Paragraph("<br/>", styles['Normal'])
        )

        # -----------------------------
        # Customer Details
        # -----------------------------

        customer_data = [

            ["Invoice No", f"INV-{order.id}"],
            ["Customer", order.name],
            ["Phone", order.phone],
            ["Address", order.address],
            ["Order Date", order.created_at.strftime("%d-%m-%Y %I:%M %p")],
            ["Order Status", order.status],
            ["Payment Status", order.payment_status],
            ["Payment ID", order.payment_id or "-"],

            ]

        customer_table = Table(
            customer_data,
            colWidths=[150, 320]
        )

        customer_table.setStyle(TableStyle([

            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#0d6efd")),
            ('TEXTCOLOR', (0,0), (0,-1), colors.white),

            ('BACKGROUND', (1,0), (1,-1), colors.whitesmoke),

            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),

            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),

            ('BOTTOMPADDING', (0,0), (-1,-1), 8),

            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),

        ]))

        elements.append(customer_table)
        elements.append(Spacer(1, 20))

        # -----------------------------
        # Products
        # -----------------------------

        data = [["Product", "Size", "Qty", "Unit Price", "Total"]]

        for item in order.items.all():

            total = item.quantity * item.price

            size_name = "-"

            if item.size:

                size_name = item.size.name

            data.append([

                item.product.name,

                size_name,

                str(item.quantity),

                f"₹ {item.price}",

                f"₹ {total}"

            ])      

        table = Table(

            data,

            colWidths=[280,80,65,90,90]

        )

        table.setStyle(TableStyle([

            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#198754")),

            ('TEXTCOLOR', (0,0), (-1,0), colors.white),

            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),

            ('BACKGROUND', (0,1), (-1,-1), colors.beige),

            ('ALIGN', (1,1), (-1,-1), 'CENTER'),

            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

            ('BOTTOMPADDING', (0,0), (-1,0), 10),

        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        # -----------------------------
        # Total
        # -----------------------------

        total_table = Table(

            [[
                "Grand Total",
                f"₹ {order.total_price}"
            ]],

            colWidths=[350,110]

        )

        total_table.setStyle(TableStyle([

            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0d6efd")),

            ('TEXTCOLOR', (0,0), (-1,-1), colors.white),

            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),

            ('FONTSIZE', (0,0), (-1,-1), 14),

            ('ALIGN', (1,0), (1,0), 'RIGHT'),

            ('BOTTOMPADDING', (0,0), (-1,-1), 10),

        ]))

        elements.append(total_table)
        elements.append(Spacer(1, 20))

       
# -----------------------------
# Footer
# -----------------------------

        footer = Paragraph("""

        <para align='center'>

        <font color='#666666' size='11'>

        <b>Thank you for shopping with VELORA STORE ❤️ </b>

        <br/>
        <br/>

        Customer Support

        <br/>

         support@velora.com

        <br/>

         +91 XXXXX XXXXX

        <br/>

         www.velora.com

        </font>

        </para>

        """, styles["Normal"])

        elements.append(footer)

        pdf.build(elements)

        buffer.seek(0)

        response = HttpResponse(
        buffer,
        content_type="application/pdf"
    )

        response[
        "Content-Disposition"
        ] = f'attachment; filename="Invoice_{order.id}.pdf"'

        return response
    


class AdminDashboardAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        total_categories = Category.objects.count()

        total_users = User.objects.count()

        total_products = Product.objects.count()

        total_orders = Order.objects.count()

        total_revenue = (
            Order.objects.filter(
                payment_status='Success'
            ).aggregate(
                total=Sum('total_price')
            )['total'] or 0
        )

        return Response({

            "total_categories": total_categories,

            "total_users": total_users,

            "total_products": total_products,

            "total_orders": total_orders

            

        })

class CheckPincodeAPIView(APIView):

    permission_classes = [permissions.AllowAny]

    def get(self, request, pincode):

        if len(str(pincode)) != 6:

            return Response({

                "success": False,

                "message": "Invalid Pincode"

            }, status=400)

        try:

            response = requests.get(

                f"https://api.postalpincode.in/pincode/{pincode}",

                headers={

                    "User-Agent": "Mozilla/5.0",

                    "Accept": "application/json"

                },

                verify=False,

                timeout=20

            )

            

            data = response.json()

            if (

                data[0]["Status"] == "Success"

                and

                data[0]["PostOffice"]

            ):

                office = data[0]["PostOffice"][0]

                return Response({

                    "success": True,

                    "state": office["State"],

                    "district": office["District"],

                    "postoffice": office["Name"]

                })

            return Response({

                "success": False,

                "message": "Delivery not available"

            })

        except Exception as e:

            import traceback

            traceback.print_exc()

            return Response({

                "success": False,

                "message": str(e)

            }, status=500)    

from django.core.management import call_command
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([IsAdminUser])
def restore_database(request):

    try:
        call_command("loaddata", "data.json")

        return Response({
            "success": True,
            "message": "Database restored successfully."
        })

    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=500)