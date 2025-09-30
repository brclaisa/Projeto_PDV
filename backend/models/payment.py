from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # cash, credit_card, debit_card, pix, etc.
    requires_approval = Column(Boolean, default=False)
    fee_percentage = Column(Float, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, name='{self.name}', type='{self.type}')>"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_methods.id"), nullable=False)
    amount = Column(Float, nullable=False)
    fee_amount = Column(Float, default=0)
    net_amount = Column(Float, nullable=False)
    authorization_code = Column(String(100))
    transaction_id = Column(String(100))
    status = Column(String(20), default="pending")  # pending, approved, declined, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))

    # Relacionamentos
    sale = relationship("Sale")
    payment_method = relationship("PaymentMethod")

    def __repr__(self):
        return f"<Payment(id={self.id}, sale_id={self.sale_id}, amount={self.amount}, status='{self.status}')>"
