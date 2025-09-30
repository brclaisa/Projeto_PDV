from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date
from backend.database import get_db
from backend.models.sale import Sale, SaleItem
from backend.models.product import Product
from backend.models.inventory import Inventory, InventoryMovement
from backend.schemas import Sale as SaleSchema, SaleCreate, SaleUpdate, SaleItem as SaleItemSchema
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

router = APIRouter()

@router.post("/", response_model=SaleSchema)
async def create_sale(sale_data: SaleCreate, db: Session = Depends(get_db)):
    """Criar uma nova venda"""
    # Calcular total dos itens
    total_amount = 0
    items_data = []
    
    for item in sale_data.items:
        # Verificar se produto existe e está ativo
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=400, 
                detail=f"Produto ID {item.product_id} não encontrado ou inativo"
            )
        
        # Verificar estoque disponível
        inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
        if inventory and inventory.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente para o produto {product.name}. Disponível: {inventory.quantity}"
            )
        
        # Calcular preços
        discount_amount = (item.unit_price * item.quantity * item.discount_percentage) / 100
        total_price = (item.unit_price * item.quantity) - discount_amount
        total_amount += total_price
        
        items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": total_price,
            "discount_percentage": item.discount_percentage,
            "discount_amount": discount_amount
        })
    
    # Criar venda
    sale = Sale(
        customer_id=sale_data.customer_id,
        total_amount=total_amount,
        discount_amount=sale_data.discount_amount or 0,
        final_amount=total_amount - (sale_data.discount_amount or 0),
        payment_method=sale_data.payment_method,
        notes=sale_data.notes
    )
    
    db.add(sale)
    db.commit()
    db.refresh(sale)
    
    # Criar itens da venda e atualizar estoque
    for item_data in items_data:
        # Criar item da venda
        sale_item = SaleItem(sale_id=sale.id, **item_data)
        db.add(sale_item)
        
        # Atualizar estoque
        inventory = db.query(Inventory).filter(Inventory.product_id == item_data["product_id"]).first()
        if inventory:
            previous_quantity = inventory.quantity
            new_quantity = previous_quantity - item_data["quantity"]
            inventory.quantity = new_quantity
            
            # Registrar movimento do estoque
            movement = InventoryMovement(
                product_id=item_data["product_id"],
                movement_type="out",
                quantity=item_data["quantity"],
                previous_quantity=previous_quantity,
                new_quantity=new_quantity,
                reason=f"Venda #{sale.id}",
                reference_id=sale.id
            )
            db.add(movement)
    
    db.commit()
    db.refresh(sale)
    
    # Buscar venda completa com itens
    return db.query(Sale).filter(Sale.id == sale.id).first()

@router.get("/", response_model=List[SaleSchema])
async def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[int] = Query(None),
    payment_status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar vendas com filtros opcionais"""
    query = db.query(Sale)
    
    if customer_id:
        query = query.filter(Sale.customer_id == customer_id)
    
    if payment_status:
        query = query.filter(Sale.payment_status == payment_status)
    
    if start_date:
        query = query.filter(func.date(Sale.created_at) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Sale.created_at) <= end_date)
    
    sales = query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
    return sales

@router.get("/{sale_id}", response_model=SaleSchema)
async def get_sale(sale_id: int, db: Session = Depends(get_db)):
    """Obter uma venda específica"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return sale

@router.put("/{sale_id}", response_model=SaleSchema)
async def update_sale(
    sale_id: int,
    sale_update: SaleUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar uma venda"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    
    update_data = sale_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sale, field, value)
    
    db.commit()
    db.refresh(sale)
    return sale

@router.get("/{sale_id}/receipt")
async def get_sale_receipt(sale_id: int, db: Session = Depends(get_db)):
    """Gerar recibo da venda"""
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    
    # Formatar dados do recibo
    receipt_data = {
        "sale_id": sale.id,
        "date": sale.created_at.strftime("%d/%m/%Y %H:%M"),
        "customer": sale.customer.name if sale.customer else "Cliente não identificado",
        "items": [
            {
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price
            }
            for item in sale.items
        ],
        "subtotal": sale.total_amount,
        "discount": sale.discount_amount,
        "total": sale.final_amount,
        "payment_method": sale.payment_method,
        "payment_status": sale.payment_status
    }
    
    return receipt_data

@router.get("/today/summary")
async def get_today_sales_summary(db: Session = Depends(get_db)):
    """Resumo de vendas do dia"""
    today = date.today()
    
    # Vendas do dia
    sales_today = db.query(Sale).filter(func.date(Sale.created_at) == today).all()
    
    total_sales = len(sales_today)
    total_amount = sum(sale.final_amount for sale in sales_today)
    
    # Vendas por método de pagamento
    payment_methods = {}
    for sale in sales_today:
        method = sale.payment_method
        if method not in payment_methods:
            payment_methods[method] = {"count": 0, "amount": 0}
        payment_methods[method]["count"] += 1
        payment_methods[method]["amount"] += sale.final_amount
    
    return {
        "date": today.strftime("%d/%m/%Y"),
        "total_sales": total_sales,
        "total_amount": total_amount,
        "payment_methods": payment_methods
    }
