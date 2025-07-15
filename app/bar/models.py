from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Bar(Base):
    __tablename__ = "bars"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BarItem(Base):
    __tablename__ = "bar_items"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("store_items.id"), nullable=False)
    bar_id = Column(Integer, ForeignKey("bars.id"), nullable=False)
    quantity = Column(Integer, default=0)
    selling_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    item = relationship("StoreItem", lazy="joined")
    bar = relationship("Bar", lazy="joined")

class BarSale(Base):
    __tablename__ = "bar_sales"
    id = Column(Integer, primary_key=True, index=True)
    bar_id = Column(Integer, ForeignKey("bars.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    sale_date = Column(DateTime, default=datetime.utcnow)

    bar = relationship("Bar")
    created_by_ = relationship("User", lazy="joined")  # renamed to avoid clash

    sale_items = relationship(
        "BarSaleItem",
        back_populates="sale",
        cascade="all, delete-orphan"
    )

    @property
    def created_by(self):
        return self.created_by_.username if self.created_by_ else None


class BarSaleItem(Base):
    __tablename__ = "bar_sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("bar_sales.id"))
    bar_item_id = Column(Integer, ForeignKey("bar_items.id"))
    quantity = Column(Integer)
    total_amount = Column(Float, nullable=True)  # ✅ Add this line

    sale = relationship("BarSale", back_populates="sale_items")
    bar_item = relationship("BarItem")
