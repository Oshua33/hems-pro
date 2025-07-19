from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base



class BarPayment(Base):
    __tablename__ = "bar_payments"

    id = Column(Integer, primary_key=True, index=True)
    bar_sale_id = Column(Integer, ForeignKey("bar_sales.id"))
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)  # Cash, POS, Transfer
    date_paid = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")  # "active" or "voided"

    bar_sale = relationship("BarSale", back_populates="payments")
