from pydantic import BaseModel, Field, PositiveFloat, confloat
from uuid import UUID
from enum import Enum


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"


class OrderStatus(str, Enum):
    CLOSED = "closed"
    OPENED = "opened"


class MenuItem(BaseModel):
    name: str = Field(..., max_length=30, description="Название блюда")
    price: PositiveFloat = Field(..., description="Цена блюда")

class MenuItemId(BaseModel):
    menu_id: UUID = Field(..., description="Уникальный идентификатор блюда")

class Order(BaseModel):
    order_id: UUID = Field(..., description="Уникальный идентификатор заказа")

class OrderUpdate(Order):
    items: list[MenuItemId] = Field(..., description="Список добавляемых блюд")

class OrderClose(Order):
    tips: confloat(ge=0) = Field(0, description="Чаевые")
    payment_method: PaymentMethod = Field(..., description="Способ оплаты")