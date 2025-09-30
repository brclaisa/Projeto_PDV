from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuração do banco de dados
DATABASE_URL = "sqlite:///./panther_pdv.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    # Importar todos os modelos para garantir que as tabelas sejam criadas
    from backend.models.product import Product, Category
    from backend.models.customer import Customer
    from backend.models.sale import Sale, SaleItem
    from backend.models.inventory import Inventory, InventoryMovement
    from backend.models.payment import PaymentMethod, Payment
    
    Base.metadata.create_all(bind=engine)
