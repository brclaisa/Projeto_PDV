from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date
from backend.database import get_db
from backend.models.payment import PaymentMethod, Payment
from backend.schemas import PaymentMethod as PaymentMethodSchema, PaymentMethodCreate
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

router = APIRouter()

@router.post("/methods/", response_model=PaymentMethodSchema)
async def create_payment_method(
    payment_method: PaymentMethodCreate, 
    db: Session = Depends(get_db)
):
    """Criar um novo método de pagamento"""
    # Verificar se já existe método com mesmo nome
    existing = db.query(PaymentMethod).filter(
        PaymentMethod.name == payment_method.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Método de pagamento já existe")
    
    db_payment_method = PaymentMethod(**payment_method.dict())
    db.add(db_payment_method)
    db.commit()
    db.refresh(db_payment_method)
    return db_payment_method

@router.get("/methods/", response_model=List[PaymentMethodSchema])
async def list_payment_methods(
    active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar métodos de pagamento"""
    query = db.query(PaymentMethod)
    
    if active is not None:
        query = query.filter(PaymentMethod.active == active)
    
    methods = query.all()
    return methods

@router.get("/methods/{method_id}", response_model=PaymentMethodSchema)
async def get_payment_method(method_id: int, db: Session = Depends(get_db)):
    """Obter um método de pagamento específico"""
    method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="Método de pagamento não encontrado")
    return method

@router.put("/methods/{method_id}", response_model=PaymentMethodSchema)
async def update_payment_method(
    method_id: int,
    name: Optional[str] = None,
    type: Optional[str] = None,
    requires_approval: Optional[bool] = None,
    fee_percentage: Optional[float] = None,
    active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Atualizar um método de pagamento"""
    method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="Método de pagamento não encontrado")
    
    if name is not None:
        # Verificar se nome já existe
        existing = db.query(PaymentMethod).filter(
            PaymentMethod.name == name,
            PaymentMethod.id != method_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Nome já existe")
        method.name = name
    
    if type is not None:
        method.type = type
    if requires_approval is not None:
        method.requires_approval = requires_approval
    if fee_percentage is not None:
        method.fee_percentage = fee_percentage
    if active is not None:
        method.active = active
    
    db.commit()
    db.refresh(method)
    return method

@router.delete("/methods/{method_id}")
async def delete_payment_method(method_id: int, db: Session = Depends(get_db)):
    """Desativar um método de pagamento"""
    method = db.query(PaymentMethod).filter(PaymentMethod.id == method_id).first()
    if not method:
        raise HTTPException(status_code=404, detail="Método de pagamento não encontrado")
    
    method.active = False
    db.commit()
    return {"message": "Método de pagamento desativado com sucesso"}

@router.post("/process/{sale_id}")
async def process_payment(
    sale_id: int,
    payment_method_id: int,
    amount: float,
    authorization_code: Optional[str] = None,
    transaction_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Processar pagamento de uma venda"""
    from backend.models.sale import Sale
    
    # Verificar se venda existe
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    
    # Verificar se método de pagamento existe
    payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.id == payment_method_id
    ).first()
    if not payment_method:
        raise HTTPException(status_code=404, detail="Método de pagamento não encontrado")
    
    # Calcular taxa se aplicável
    fee_amount = (amount * payment_method.fee_percentage) / 100
    net_amount = amount - fee_amount
    
    # Criar pagamento
    payment = Payment(
        sale_id=sale_id,
        payment_method_id=payment_method_id,
        amount=amount,
        fee_amount=fee_amount,
        net_amount=net_amount,
        authorization_code=authorization_code,
        transaction_id=transaction_id,
        status="approved" if not payment_method.requires_approval else "pending"
    )
    
    db.add(payment)
    
    # Atualizar status da venda se pagamento aprovado
    if payment.status == "approved":
        sale.payment_status = "paid"
    
    db.commit()
    db.refresh(payment)
    
    return {
        "payment_id": payment.id,
        "status": payment.status,
        "amount": payment.amount,
        "net_amount": payment.net_amount,
        "fee_amount": payment.fee_amount
    }

@router.get("/transactions/", response_model=List[dict])
async def list_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sale_id: Optional[int] = Query(None),
    payment_method_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar transações de pagamento"""
    query = db.query(Payment)
    
    if sale_id:
        query = query.filter(Payment.sale_id == sale_id)
    
    if payment_method_id:
        query = query.filter(Payment.payment_method_id == payment_method_id)
    
    if status:
        query = query.filter(Payment.status == status)
    
    if start_date:
        query = query.filter(func.date(Payment.created_at) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Payment.created_at) <= end_date)
    
    payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": payment.id,
            "sale_id": payment.sale_id,
            "payment_method": payment.payment_method.name,
            "amount": payment.amount,
            "fee_amount": payment.fee_amount,
            "net_amount": payment.net_amount,
            "status": payment.status,
            "authorization_code": payment.authorization_code,
            "transaction_id": payment.transaction_id,
            "created_at": payment.created_at,
            "processed_at": payment.processed_at
        }
        for payment in payments
    ]

@router.get("/summary")
async def get_payments_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Resumo de pagamentos por método"""
    query = db.query(Payment).join(PaymentMethod)
    
    if start_date:
        query = query.filter(func.date(Payment.created_at) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Payment.created_at) <= end_date)
    
    payments = query.filter(Payment.status == "approved").all()
    
    summary = {}
    total_amount = 0
    total_fees = 0
    
    for payment in payments:
        method_name = payment.payment_method.name
        
        if method_name not in summary:
            summary[method_name] = {
                "count": 0,
                "total_amount": 0,
                "total_fees": 0,
                "net_amount": 0
            }
        
        summary[method_name]["count"] += 1
        summary[method_name]["total_amount"] += payment.amount
        summary[method_name]["total_fees"] += payment.fee_amount
        summary[method_name]["net_amount"] += payment.net_amount
        
        total_amount += payment.amount
        total_fees += payment.fee_amount
    
    return {
        "period": {
            "start_date": start_date.strftime("%d/%m/%Y") if start_date else None,
            "end_date": end_date.strftime("%d/%m/%Y") if end_date else None
        },
        "summary": summary,
        "totals": {
            "total_amount": total_amount,
            "total_fees": total_fees,
            "net_amount": total_amount - total_fees,
            "total_transactions": len(payments)
        }
    }
