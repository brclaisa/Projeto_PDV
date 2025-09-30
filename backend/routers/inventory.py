from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date
from backend.database import get_db
from backend.models.inventory import Inventory, InventoryMovement
from backend.models.product import Product
from backend.schemas import Inventory as InventorySchema, InventoryCreate, InventoryUpdate, InventoryAdjust
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

router = APIRouter()

@router.post("/", response_model=InventorySchema)
async def create_inventory(inventory: InventoryCreate, db: Session = Depends(get_db)):
    """Criar ou atualizar inventário de um produto"""
    # Verificar se produto existe
    product = db.query(Product).filter(Product.id == inventory.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Verificar se já existe inventário para o produto
    existing_inventory = db.query(Inventory).filter(
        Inventory.product_id == inventory.product_id
    ).first()
    
    if existing_inventory:
        # Atualizar inventário existente
        previous_quantity = existing_inventory.quantity
        existing_inventory.quantity = inventory.quantity
        existing_inventory.min_stock = inventory.min_stock
        existing_inventory.max_stock = inventory.max_stock
        existing_inventory.location = inventory.location
        existing_inventory.last_updated = datetime.now()
        
        # Registrar movimento se quantidade mudou
        if previous_quantity != inventory.quantity:
            movement = InventoryMovement(
                product_id=inventory.product_id,
                movement_type="adjustment",
                quantity=inventory.quantity - previous_quantity,
                previous_quantity=previous_quantity,
                new_quantity=inventory.quantity,
                reason="Ajuste manual de estoque"
            )
            db.add(movement)
        
        db.commit()
        db.refresh(existing_inventory)
        return existing_inventory
    else:
        # Criar novo inventário
        db_inventory = Inventory(**inventory.dict())
        db.add(db_inventory)
        
        # Registrar movimento inicial
        movement = InventoryMovement(
            product_id=inventory.product_id,
            movement_type="in",
            quantity=inventory.quantity,
            previous_quantity=0,
            new_quantity=inventory.quantity,
            reason="Estoque inicial"
        )
        db.add(movement)
        
        db.commit()
        db.refresh(db_inventory)
        return db_inventory

@router.get("/", response_model=List[InventorySchema])
async def list_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    low_stock: Optional[bool] = Query(None),
    product_name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar inventário com filtros opcionais"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Inventory).options(joinedload(Inventory.product))
    
    if low_stock:
        query = query.filter(Inventory.quantity <= Inventory.min_stock)
    
    if product_name:
        query = query.join(Product).filter(Product.name.contains(product_name))
    
    inventory = query.offset(skip).limit(limit).all()
    return inventory

@router.get("/product/{product_id}", response_model=InventorySchema)
async def get_product_inventory(product_id: int, db: Session = Depends(get_db)):
    """Obter inventário de um produto específico"""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventário não encontrado para este produto")
    return inventory

@router.put("/{inventory_id}", response_model=InventorySchema)
async def update_inventory(
    inventory_id: int,
    inventory_update: InventoryUpdate,
    db: Session = Depends(get_db)
):
    """Atualizar inventário"""
    inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventário não encontrado")
    
    update_data = inventory_update.dict(exclude_unset=True)
    
    # Registrar movimento se quantidade mudou
    if "quantity" in update_data and update_data["quantity"] != inventory.quantity:
        previous_quantity = inventory.quantity
        new_quantity = update_data["quantity"]
        
        movement = InventoryMovement(
            product_id=inventory.product_id,
            movement_type="adjustment",
            quantity=new_quantity - previous_quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reason="Ajuste manual de estoque"
        )
        db.add(movement)
    
    for field, value in update_data.items():
        setattr(inventory, field, value)
    
    inventory.last_updated = datetime.now()
    db.commit()
    db.refresh(inventory)
    return inventory

@router.post("/adjust/{product_id}")
async def adjust_inventory(
    product_id: int,
    payload: InventoryAdjust,
    db: Session = Depends(get_db)
):
    """Ajustar quantidade do inventário (define a quantidade final)."""
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventário não encontrado")

    previous_quantity = inventory.quantity
    new_quantity = payload.quantity

    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Quantidade não pode ser negativa")

    inventory.quantity = new_quantity
    inventory.last_updated = datetime.now()

    # Registrar movimento (diferença)
    movement = InventoryMovement(
        product_id=product_id,
        movement_type="adjustment",
        quantity=new_quantity - previous_quantity,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reason=payload.reason
    )
    db.add(movement)

    db.commit()
    return {"message": f"Estoque ajustado de {previous_quantity} para {new_quantity}"}

@router.get("/movements/{product_id}")
async def get_product_movements(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Obter movimentações de estoque de um produto"""
    movements = db.query(InventoryMovement).filter(
        InventoryMovement.product_id == product_id
    ).order_by(InventoryMovement.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": movement.id,
            "movement_type": movement.movement_type,
            "quantity": movement.quantity,
            "previous_quantity": movement.previous_quantity,
            "new_quantity": movement.new_quantity,
            "reason": movement.reason,
            "reference_id": movement.reference_id,
            "created_at": movement.created_at
        }
        for movement in movements
    ]

@router.get("/low-stock")
async def get_low_stock_products(db: Session = Depends(get_db)):
    """Listar produtos com estoque baixo"""
    low_stock = db.query(Inventory).join(Product).filter(
        Inventory.quantity <= Inventory.min_stock,
        Product.active == True
    ).all()
    
    return [
        {
            "product_id": inv.product_id,
            "product_name": inv.product.name,
            "current_quantity": inv.quantity,
            "min_stock": inv.min_stock,
            "location": inv.location
        }
        for inv in low_stock
    ]

@router.get("/summary")
async def get_inventory_summary(db: Session = Depends(get_db)):
    """Resumo do inventário"""
    total_products = db.query(Product).filter(Product.active == True).count()
    total_inventory = db.query(Inventory).count()
    
    # Produtos com estoque baixo
    low_stock_count = db.query(Inventory).filter(
        Inventory.quantity <= Inventory.min_stock
    ).count()
    
    # Valor total do estoque
    total_value = db.query(
        func.sum(Inventory.quantity * Product.price)
    ).join(Product).filter(Product.active == True).scalar() or 0
    
    return {
        "total_products": total_products,
        "total_inventory": total_inventory,
        "low_stock_count": low_stock_count,
        "total_value": total_value
    }
