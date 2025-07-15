from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# ----------------------------
# 1. Store Category
# ----------------------------
class StoreCategory(Base):
    __tablename__ = "store_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ----------------------------
# 2. Store Item
# ----------------------------
class StoreItem(Base):
    __tablename__ = "store_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    unit = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("store_categories.id"), nullable=True)
    category = relationship("StoreCategory")

    created_at = Column(DateTime, default=datetime.utcnow)

    # Optional: create relationship if you store category_id instead of name
    # category_id = Column(Integer, ForeignKey("store_categories.id"), nullable=True)
    # category = relationship("StoreCategory")


# ----------------------------
# 3. Store Stock Entry (Purchase)
# ----------------------------
class StoreStockEntry(Base):
    __tablename__ = "store_stock_entries"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("store_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=True)  # ✅ new
    vendor = Column(String, nullable=True)
    purchase_date = Column(DateTime, default=datetime.utcnow)

    item = relationship("StoreItem")


# ----------------------------
# 4. Store Issue
# ----------------------------
class StoreIssue(Base):
    __tablename__ = "store_issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_to = Column(String, nullable=False)  # "bar" or "restaurant"
    issued_to_id = Column(Integer, nullable=False)  # ✅ ADD THIS LINE
    issued_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    issue_date = Column(DateTime, default=datetime.utcnow)

    issue_items = relationship("StoreIssueItem", back_populates="issue", cascade="all, delete-orphan")


class StoreIssueItem(Base):
    __tablename__ = "store_issue_items"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("store_issues.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("store_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    


    issue = relationship("StoreIssue", back_populates="issue_items")
    item = relationship("StoreItem")
