from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# ----------------------------
# Bar
# ----------------------------
class Bar(Base):
    __tablename__ = "bars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ----------------------------
# Bar Inventory (auto quantity updates from StoreIssue)
# ----------------------------
class BarInventory(Base):
    __tablename__ = "bar_inventory"

    id = Column(Integer, primary_key=True, index=True)
    bar_id = Column(Integer, ForeignKey("bars.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("store_items.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    selling_price = Column(Float, default=0)

    bar = relationship("Bar", backref="inventory")
    item = relationship("StoreItem")

    __table_args__ = (
        UniqueConstraint("bar_id", "item_id", name="unique_bar_item"),
    )


# ----------------------------
# Bar Sale
# ----------------------------
class BarSale(Base):
    __tablename__ = "bar_sales"

    id = Column(Integer, primary_key=True, index=True)
    bar_id = Column(Integer, ForeignKey("bars.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    sale_date = Column(DateTime, default=datetime.utcnow)

    bar = relationship("Bar")
    created_by_ = relationship("User", lazy="joined")

    sale_items = relationship(
        "BarSaleItem",
        back_populates="sale",
        cascade="all, delete-orphan"
    )

    @property
    def created_by(self):
        return self.created_by_.username if self.created_by_ else None


# ----------------------------
# Bar Sale Item
# ----------------------------
class BarSaleItem(Base):
    __tablename__ = "bar_sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("bar_sales.id"))
    bar_inventory_id = Column(Integer, ForeignKey("bar_inventory.id"))
    quantity = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)

    sale = relationship("BarSale", back_populates="sale_items")
    bar_inventory = relationship("BarInventory")
