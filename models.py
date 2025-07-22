from pydantic import BaseModel
from uuid import UUID


class MenuItem(BaseModel):
    name: str
    price: float

class OrderItem(BaseModel):
    menu_id: UUID

class Order(BaseModel):
    order_id: UUID

class OrderUpdate(Order):
    items: list[OrderItem]

class OrderClose(Order):
    order_id: UUID
    tips: float
    payment_method: str