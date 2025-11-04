from sqlalchemy import Boolean, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users import User
    from .products import Product

class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    

    user: Mapped['User'] = relationship('User', back_populates='reviews')
    product: Mapped['Product'] = relationship('Product', back_populates='reviews')