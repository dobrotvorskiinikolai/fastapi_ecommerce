from decimal import Decimal
from sqlalchemy import String, Boolean, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship  
from sqlalchemy import ForeignKey  
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .categories import Category

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False) 

    category: Mapped["Category"] = relationship(back_populates="products")