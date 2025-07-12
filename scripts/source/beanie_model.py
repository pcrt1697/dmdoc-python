from datetime import date, datetime, time
from decimal import Decimal
from enum import StrEnum, Enum
from typing import Optional, Union

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

from dmdoc.core.sink.model import EntityReference, FieldReference


class _Collections:
    USERS = "users"
    PRODUCTS = "products"
    ORDERS = "orders"


class Country(StrEnum):
    IT = "IT"
    DE = "DE"
    US = "US"


class CardVendor(StrEnum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMERICAN_EXPRESS = "AMERICAN_EXPRESS"


class OrderStatus(Enum):
    DRAFT = 1
    CREATED = 2
    SHIPPED = 3
    DELIVERED = 4


class AuditMeta(BaseModel):
    ts_insert: datetime = Field(description="Document creation date")
    ts_update: datetime = Field(description="Last update date")


class User(Document):
    id: str = Field(description="User email that represents the user identifier")
    name: str = Field(description="Name of the user")
    address: Optional["Address"] = Field(description="First name of the user", default=None)
    credit_cards: list["CreditCard"] = Field(description="Payment methods saved by user", default=[])
    audit: AuditMeta = Field(description="Update/insert document metadata")

    class Settings:
        name = "users"


class Address(BaseModel):
    country: Country = Field(description="Country identifier")
    location: str = Field(description="Address name")
    city: str = Field(description="City name")


class CreditCard(BaseModel):
    vendor: CardVendor = Field(description="Vendor identifier")
    number: str = Field(description="Card number")
    expiration_date: date


class Product(Document):
    name: str = Field(description="Product name")
    description: Optional[str] = Field(default=None)
    price: Decimal
    height: float | None
    width: float | None
    additional_names: set[str]
    image: bytes
    properties: dict[str, str] = Field(description="Additional properties of the product", default={})
    audit: AuditMeta = Field(description="Update/insert document metadata")

    class Settings:
        name = _Collections.PRODUCTS


class OrderItem(BaseModel):
    id_product: PydanticObjectId
    quantity: int


class OrderTransaction(BaseModel):
    credit_card: str
    amount: Decimal


class Order(Document):
    id_user: str
    status: OrderStatus
    confirmation_date: Optional[datetime]
    shipping_date: Optional[datetime]
    delivery_date: Optional[datetime]
    items: list["OrderItem"] = Field(description="List of products", min_length=1)
    transaction: "OrderTransaction"
    audit: AuditMeta = Field(description="Update/insert document metadata")

    class Settings:
        name = _Collections.ORDERS

    class DmDocConfig:
        references = [
            EntityReference(
                id_entity=_Collections.USERS,
                mapping=[
                    FieldReference(
                        source="transaction.credit_card",
                        destination="credit_cards.number"
                    )
                ]
            ),
            EntityReference(
                id_entity=_Collections.USERS,
                mapping=[
                    FieldReference(
                        source="id_user",
                        destination="id"
                    )
                ]
            ),
            EntityReference(
                id_entity=_Collections.PRODUCTS,
                mapping=[
                    FieldReference(
                        source="items.id_product",
                        destination="id"
                    )
                ]
            )
        ]


document_models = [User, Product, Order]
