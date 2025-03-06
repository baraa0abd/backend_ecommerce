from ninja import Schema
from pydantic import Field
from typing import Optional

from pydantic import BaseModel, EmailStr

class SignUpSchema(BaseModel):
    username: str
    password: str
    email: EmailStr

class LoginSchema(BaseModel):
    username: str
    password: str

class MessageResponse(BaseModel):
    message: str

class LoginResponse(BaseModel):
    token: str


class ProductSchema(Schema):
    id: Optional[int]
    name: str
    description: str
    price: float
    brand: str
    image: Optional[str]

class OrderSchema(Schema):
    id: Optional[int]
    product_id: int
    quantity: int

class CartItemSchema(Schema):
    id: Optional[int]
    product_id: int
    quantity: int

class ReviewSchema(Schema):
    id: Optional[int]
    product_id: int
    rating: int
    comment: Optional[str]

class CategorySchema(Schema):
    id: Optional[int]
    name: str
    description: str