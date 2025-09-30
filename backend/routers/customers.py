from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.customer import Customer
from backend.schemas import Customer as CustomerSchema, CustomerCreate, CustomerUpdate
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

router = APIRouter()

@router.post("/", response_model=CustomerSchema)
async def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    """Criar um novo cliente"""
    # Verificar se já existe cliente com mesmo email ou documento
    if customer.email:
        existing_email = db.query(Customer).filter(Customer.email == customer.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    if customer.document:
        existing_doc = db.query(Customer).filter(Customer.document == customer.document).first()
        if existing_doc:
            raise HTTPException(status_code=400, detail="Documento já cadastrado")
    
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=List[CustomerSchema])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar clientes com filtros opcionais"""
    query = db.query(Customer)
    
    if search:
        query = query.filter(
            Customer.name.contains(search) |
            Customer.email.contains(search) |
            Customer.document.contains(search)
        )
    
    if active is not None:
        query = query.filter(Customer.active == active)
    
    customers = query.offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=CustomerSchema)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Obter um cliente específico"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer

@router.put("/{customer_id}", response_model=CustomerSchema)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar um cliente"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verificar duplicatas em email e documento
    update_data = customer_update.dict(exclude_unset=True)
    
    if "email" in update_data and update_data["email"]:
        existing_email = db.query(Customer).filter(
            Customer.email == update_data["email"],
            Customer.id != customer_id
        ).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    if "document" in update_data and update_data["document"]:
        existing_doc = db.query(Customer).filter(
            Customer.document == update_data["document"],
            Customer.id != customer_id
        ).first()
        if existing_doc:
            raise HTTPException(status_code=400, detail="Documento já cadastrado")
    
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{customer_id}")
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """Deletar um cliente (soft delete)"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    customer.active = False
    db.commit()
    return {"message": "Cliente desativado com sucesso"}

@router.get("/document/{document}", response_model=CustomerSchema)
async def get_customer_by_document(document: str, db: Session = Depends(get_db)):
    """Obter cliente por CPF/CNPJ"""
    customer = db.query(Customer).filter(Customer.document == document).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer

@router.get("/email/{email}", response_model=CustomerSchema)
async def get_customer_by_email(email: str, db: Session = Depends(get_db)):
    """Obter cliente por email"""
    customer = db.query(Customer).filter(Customer.email == email).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer
