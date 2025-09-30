from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    min_stock = Column(Integer, default=0)
    max_stock = Column(Integer)
    location = Column(String(100))
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento
    product = relationship("Product", back_populates="inventory")

    def __repr__(self):
        return f"<Inventory(product_id={self.product_id}, quantity={self.quantity})>"

class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    movement_type = Column(String(20), nullable=False)  # 'in', 'out', 'adjustment'
    quantity = Column(Integer, nullable=False)
    previous_quantity = Column(Integer)
    new_quantity = Column(Integer)
    reason = Column(String(255))
    reference_id = Column(Integer)  # ID da venda ou compra
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento
    product = relationship("Product")

    def __repr__(self):
        return f"<InventoryMovement(product_id={self.product_id}, type='{self.movement_type}', quantity={self.quantity})>"
