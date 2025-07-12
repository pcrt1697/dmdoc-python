import enum
from datetime import datetime, date
from decimal import Decimal
from typing import List
from sqlalchemy import ForeignKey, Table, Column, Integer, Enum, LargeBinary
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, registry
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class CountryEnum(enum.StrEnum):
    IT = "IT"
    DE = "DE"
    US = "US"


class CardVendor(enum.StrEnum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMERICAN_EXPRESS = "AMERICAN_EXPRESS"


class OrderStatus(enum.Enum):
    DRAFT = 1
    CREATED = 2
    SHIPPED = 3
    DELIVERED = 4


class Base(DeclarativeBase):
    pass


class AuditMixin:
    ts_insert: Mapped[datetime]
    ts_update: Mapped[datetime]


class User(Base, AuditMixin):
    __tablename__ = "users"
    __table_args__ = {
        'comment': 'Table that contains all users'
    }

    id: Mapped[str] = mapped_column(primary_key=True, comment="User email that represents the user identifier")
    name: Mapped[str] = mapped_column(String(30), nullable=True)

    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Address(Base, AuditMixin):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    country: Mapped[CountryEnum] = mapped_column(Enum(CountryEnum), comment="Country identifier")
    location: Mapped[str] = mapped_column(comment="Address name")
    city: Mapped[str] = mapped_column(comment="City name")

    user: Mapped["User"] = relationship(back_populates="addresses")


class CreditCard(Base, AuditMixin):
    __tablename__ = "credit_cards"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    vendor: Mapped[CardVendor] = mapped_column(Enum(CardVendor), comment="Vendor identifier")
    number: Mapped[str] = mapped_column(comment="Card number")
    expiration_date: Mapped[date] = mapped_column()
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id"))


class Product(Base, AuditMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(comment="Product name")
    description: Mapped[str] = mapped_column(comment="Description of the product", nullable=True)
    price: Mapped[Decimal] = mapped_column()
    height: Mapped[float] = mapped_column(nullable=True)
    width: Mapped[float] = mapped_column(nullable=True)
    image: Mapped[bytes] = mapped_column(LargeBinary)


class Order(Base, AuditMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus))
    confirmation_date: Mapped[datetime] = mapped_column(nullable=True)
    shipping_date: Mapped[datetime] = mapped_column(nullable=True)
    delivery_date: Mapped[datetime] = mapped_column(nullable=True)

    items: Mapped[List["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_order: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    id_product: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]

    order: Mapped["Order"] = relationship(back_populates="items")


mapper_registry = Base.registry

country_table = Table(
    "countries",
    mapper_registry.metadata,
    Column("id", Integer, primary_key=True),
    Column("name", Enum(CountryEnum)),
    comment="An example of imperative mapping"
)


class Country:
    pass


mapper_registry.map_imperatively(Country, country_table)
