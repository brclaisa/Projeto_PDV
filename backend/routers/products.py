from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.product import Product, Category
from backend.schemas import Product as ProductSchema, ProductCreate, ProductUpdate
import sys
import os

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

router = APIRouter()

@router.post("/", response_model=ProductSchema)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Criar um novo produto"""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[ProductSchema])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Listar produtos com filtros opcionais"""
    query = db.query(Product)
    
    if search:
        query = query.filter(
            Product.name.contains(search) | 
            Product.barcode.contains(search)
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    if active is not None:
        query = query.filter(Product.active == active)
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductSchema)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obter um produto específico"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int, 
    product_update: ProductUpdate, 
    db: Session = Depends(get_db)
):
    """Atualizar um produto"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Deletar um produto (soft delete)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    product.active = False
    db.commit()
    return {"message": "Produto desativado com sucesso"}

@router.get("/barcode/{barcode}", response_model=ProductSchema)
async def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    """Obter produto por código de barras"""
    product = db.query(Product).filter(Product.barcode == barcode).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product

@router.get("/categories/list")
async def list_categories(db: Session = Depends(get_db)):
    """Listar todas as categorias"""
    categories = db.query(Product.category).filter(
        Product.category.isnot(None),
        Product.active == True
    ).distinct().all()
    return [cat[0] for cat in categories]
