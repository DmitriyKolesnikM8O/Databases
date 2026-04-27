from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date
from decimal import Decimal


# Category
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=256)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# User
class UserBase(BaseModel):
    first_name: str = Field(..., max_length=256)
    last_name: Optional[str] = Field(None, max_length=256)
    patronymic: Optional[str] = Field(None, max_length=256)
    login: str = Field(..., max_length=256)
    password_hash: str = Field(..., max_length=256)
    phone: str = Field(..., max_length=20)
    city: str = Field(..., max_length=100)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=256)
    last_name: Optional[str] = Field(None, max_length=256)
    patronymic: Optional[str] = Field(None, max_length=256)
    login: Optional[str] = Field(None, max_length=256)
    password_hash: Optional[str] = Field(None, max_length=256)
    phone: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Equipment
class EquipmentBase(BaseModel):
    owner_id: int
    category_id: int
    name: str = Field(..., max_length=256)
    description: Optional[str] = None
    price_per_day: Decimal = Field(..., decimal_places=2)
    total_quantity: int = Field(..., ge=0)


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    owner_id: Optional[int] = None
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = None
    price_per_day: Optional[Decimal] = Field(None, decimal_places=2)
    total_quantity: Optional[int] = Field(None, ge=0)


class EquipmentResponse(EquipmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Rental
class RentalBase(BaseModel):
    renter_id: int
    start_date: date
    end_date: date
    status: str = Field(default="Новый", max_length=50)


class RentalCreate(RentalBase):
    pass


class RentalUpdate(BaseModel):
    renter_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)


class RentalResponse(RentalBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class RentalItemBase(BaseModel):
    rental_id: int
    equipment_id: int
    quantity: int = Field(..., gt=0)
    price_at_booking: Decimal = Field(..., decimal_places=2)


class RentalItemCreate(RentalItemBase):
    pass


class RentalItemResponse(RentalItemBase):
    model_config = ConfigDict(from_attributes=True)


# Payment
class PaymentBase(BaseModel):
    rental_id: int
    payment_amount: Decimal = Field(..., decimal_places=2)
    payment_date: date
    status: str = Field(..., max_length=50)


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Review
class ReviewBase(BaseModel):
    renter_id: int
    equipment_id: int
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None
    created_at: date


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Pagination
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    limit: int
    pages: int
