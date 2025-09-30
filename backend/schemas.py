from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    cost_price: Optional[float] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    active: Optional[bool] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    document: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    address_street: Optional[str] = None
    address_number: Optional[str] = None
    address_complement: Optional[str] = None
    address_neighborhood: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zipcode: Optional[str] = None
    notes: Optional[str] = None
    active: bool = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    document: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    address_street: Optional[str] = None
    address_number: Optional[str] = None
    address_complement: Optional[str] = None
    address_neighborhood: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zipcode: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[bool] = None

class Customer(CustomerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Sale Item Schema
class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    discount_percentage: Optional[float] = 0

class SaleItem(SaleItemCreate):
    id: int
    total_price: float
    discount_amount: float

    class Config:
        from_attributes = True

# Sale Schemas
class SaleCreate(BaseModel):
    customer_id: Optional[int] = None
    items: List[SaleItemCreate]
    payment_method: str
    discount_amount: Optional[float] = 0
    notes: Optional[str] = None

class SaleUpdate(BaseModel):
    payment_status: Optional[str] = None
    notes: Optional[str] = None

class Sale(SaleCreate):
    id: int
    total_amount: float
    final_amount: float
    payment_status: str
    nfce_number: Optional[str] = None
    nfce_key: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[SaleItem] = []

    class Config:
        from_attributes = True

# Inventory Schemas
class InventoryBase(BaseModel):
    product_id: int
    quantity: int
    min_stock: Optional[int] = 0
    max_stock: Optional[int] = None
    location: Optional[str] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    location: Optional[str] = None

class Inventory(InventoryBase):
    id: int
    last_updated: datetime
    product: Optional[Product] = None

    class Config:
        from_attributes = True

# Inventory Adjust Schema (para POST /inventory/adjust/{product_id})
class InventoryAdjust(BaseModel):
    quantity: int  # quantidade final desejada
    reason: str

# Payment Method Schemas
class PaymentMethodBase(BaseModel):
    name: str
    type: str
    requires_approval: bool = False
    fee_percentage: float = 0
    active: bool = True

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethod(PaymentMethodBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
