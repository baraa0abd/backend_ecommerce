from ninja_extra import NinjaExtraAPI, api_controller, route, status
from ninja.security import HttpBearer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from typing import List
from rest_framework.authtoken.models import Token
from .models import  Register, Products, Orders, Cart, Category, Review
from .Schema import (
    MessageResponse,
    SignUpSchema,
    LoginSchema,
    LoginResponse,
    ProductSchema,
    OrderSchema,
    CartItemSchema,
    CategorySchema,
    ReviewSchema,
)

# API instance
api = NinjaExtraAPI()

# Security class for Bearer Authentication
class BearerAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            user_token = Token.objects.get(key=token)
            request.user = user_token.user
            return user_token.user
        except Token.DoesNotExist:
            return None

# Signup API
@api.post("/signup", response={200: MessageResponse, 400: MessageResponse})
def signup(request, payload: SignUpSchema):
    # Check if the username already exists
    if User.objects.filter(username=payload.username).exists():
        return 400, {"message": "Username already exists"}
    
    # Validate the password
    try:
        validate_password(payload.password)
    except ValidationError as e:
        return 400, {"message": " ".join(e.messages)}
    
    # Create the user
    try:
        user = User.objects.create_user(
            username=payload.username,
            password=payload.password,
            email=payload.email
        )
        user.save()
        return 200, {"message": "User created successfully"}
    except IntegrityError:
        return 400, {"message": "Error creating user"}

# Login API
@api.post("/login", response={200: LoginResponse, 401: MessageResponse})
def login_user(request, payload: LoginSchema):
    user = authenticate(username=payload.username, password=payload.password)
    if user is not None:
        if not user.is_active:
            return 401, {"message": "User account is inactive"}
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)
        return 200, {"token": token.key}
    return 401, {"message": "Invalid username or password"}

# Logout API
@api.post("/logout", auth=BearerAuth(), response={200: MessageResponse})
def logout_user(request):
    # Delete the user's token
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
    except Token.DoesNotExist:
        return 400, {"message": "Token not found"}
    
    # Log out the user
    logout(request)
    return 200, {"message": "Successfully logged out"}

@api_controller("/user", tags=["User Authentication APIs"])
class UserAuthenticationController:
    @route.post("/register", response={201: SignUpSchema, 409: MessageResponse}, auth=None)
    def register(self, request, payload: SignUpSchema):
        if Register.objects.filter(email=payload.email).exists():
            return 409, {"message": "Email already exists"}
        else:
            user = Register.objects.create(
                username=payload.username,
                email=payload.email,
                password=payload.password
            )
            return 201, user

    @route.post("/login", response={200: LoginResponse, 404: MessageResponse}, auth=None)
    def login(self, request, payload: LoginSchema):
        user = authenticate(username=payload.username, password=payload.password)
        if user:
            return 200, {"message": "Login Successful", "user": LoginResponse.from_orm(user)}
        else:
            return 404, {"message": "Login Failed"}

@api_controller("/products", tags=["Product Management APIs"], auth=BearerAuth())
class ProductController:
    @route.post("/", response={201: ProductSchema, 409: MessageResponse})
    def create_product(self, request, payload: ProductSchema):
        if Products.objects.filter(name=payload.name).exists():
            return 409, {"message": "Product already exists"}
        else:
            product = Products.objects.create(**payload.dict())
            return 201, product

    @route.get("/", response=List[ProductSchema])
    def list_products(self, request):
        products = Products.objects.all()
        return products

    @route.get("/{product_id}", response=ProductSchema)
    def get_product(self, request, product_id: int):
        product = get_object_or_404(Products, id=product_id)
        return product

    @route.put("/{product_id}", response=ProductSchema)
    def update_product(self, request, product_id: int, payload: ProductSchema):
        product = get_object_or_404(Products, id=product_id)
        for attr, value in payload.dict().items():
            setattr(product, attr, value)
        product.save()
        return product

    @route.delete("/{product_id}", response={204: None})
    def delete_product(self, request, product_id: int):
        product = get_object_or_404(Products, id=product_id)
        product.delete()
        return 204, None

@api_controller("/orders", tags=["Order Management APIs"], auth=BearerAuth())
class OrderController:
    @route.post("/", response=OrderSchema)
    def create_order(self, request, payload: OrderSchema):
        order = Orders.objects.create(**payload.dict())
        return order

    @route.get("/", response=List[OrderSchema])
    def list_orders(self, request):
        orders = Orders.objects.all()
        return orders

    @route.get("/{order_id}", response=OrderSchema)
    def get_order(self, request, order_id: int):
        order = get_object_or_404(Orders, id=order_id)
        return order

    @route.put("/{order_id}", response=OrderSchema)
    def update_order(self, request, order_id: int, payload: OrderSchema):
        order = get_object_or_404(Orders, id=order_id)
        for attr, value in payload.dict().items():
            setattr(order, attr, value)
        order.save()
        return order

    @route.delete("/{order_id}", response={204: None})
    def delete_order(self, request, order_id: int):
        order = get_object_or_404(Orders, id=order_id)
        order.delete()
        return 204, None

@api_controller("/cart", tags=["Cart Management APIs"], auth=BearerAuth())
class CartController:
    @route.post("/", response=CartItemSchema)
    def add_to_cart(self, request, payload: CartItemSchema):
        cart_item = Cart.objects.create(**payload.dict())
        return cart_item

    @route.get("/", response=List[CartItemSchema])
    def view_cart(self, request):
        cart_items = Cart.objects.all()
        return cart_items

    @route.put("/{item_id}", response=CartItemSchema)
    def update_cart_item(self, request, item_id: int, payload: CartItemSchema):
        cart_item = get_object_or_404(Cart, id=item_id)
        for attr, value in payload.dict().items():
            setattr(cart_item, attr, value)
        cart_item.save()
        return cart_item

    @route.delete("/{item_id}", response={204: None})
    def remove_from_cart(self, request, item_id: int):
        cart_item = get_object_or_404(Cart, id=item_id)
        cart_item.delete()
        return 204, None

@api_controller("/categories", tags=["Category Management APIs"])
class CategoryController:
    @route.post("/", response={201: CategorySchema})
    def create_category(self, request, payload: CategorySchema):
        category = Category.objects.create(**payload.dict())
        return 201, category

    @route.get("/", response=List[CategorySchema])
    def list_categories(self, request):
        categories = Category.objects.all()
        return categories

    @route.get("/{category_id}", response=CategorySchema)
    def get_category(self, request, category_id: int):
        category = get_object_or_404(Category, id=category_id)
        return category

    @route.put("/{category_id}", response=CategorySchema)
    def update_category(self, request, category_id: int, payload: CategorySchema):
        category = get_object_or_404(Category, id=category_id)
        for attr, value in payload.dict().items():
            setattr(category, attr, value)
        category.save()
        return category

    @route.delete("/{category_id}", response={204: None})
    def delete_category(self, request, category_id: int):
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return 204, None

@api_controller("/products/{product_id}/reviews", tags=["Review and Rating APIs"])
class ReviewController:
    @route.post("/", response={201: ReviewSchema})
    def add_review(self, request, product_id: int, payload: ReviewSchema):
        review = Review.objects.create(product_id=product_id, **payload.dict())
        return 201, review

    @route.get("/", response=List[ReviewSchema])
    def list_reviews(self, request, product_id: int):
        reviews = Review.objects.filter(product_id=product_id)
        return reviews

    @route.put("/{review_id}", response=ReviewSchema)
    def update_review(self, request, product_id: int, review_id: int, payload: ReviewSchema):
        review = get_object_or_404(Review, id=review_id, product_id=product_id)
        for attr, value in payload.dict().items():
            setattr(review, attr, value)
        review.save()
        return review

    @route.delete("/{review_id}", response={204: None})
    def delete_review(self, request, product_id: int, review_id: int):
        review = get_object_or_404(Review, id=review_id, product_id=product_id)
        review.delete()
        return 204, None

# Register all controllers with the API instance
api.register_controllers(
    UserAuthenticationController,
    ProductController,
    OrderController,
    CartController,
    CategoryController,
    ReviewController
)