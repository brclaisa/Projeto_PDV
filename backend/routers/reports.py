from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from datetime import datetime, date, timedelta
from backend.database import get_db
from backend.models.sale import Sale, SaleItem
from backend.models.product import Product
from backend.models.customer import Customer
from backend.models.inventory import Inventory
from backend.models.payment import Payment, PaymentMethod
import io
import csv
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

router = APIRouter()

@router.get("/sales")
async def sales_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db)
):
    """Relatório de vendas"""
    query = db.query(Sale)
    
    if start_date:
        query = query.filter(func.date(Sale.created_at) >= start_date)
    else:
        # Padrão: últimos 30 dias
        query = query.filter(Sale.created_at >= datetime.now() - timedelta(days=30))
    
    if end_date:
        query = query.filter(func.date(Sale.created_at) <= end_date)
    
    sales = query.order_by(Sale.created_at.desc()).all()
    
    report_data = []
    total_sales = 0
    total_amount = 0
    
    for sale in sales:
        report_data.append({
            "id": sale.id,
            "date": sale.created_at.strftime("%d/%m/%Y %H:%M"),
            "customer": sale.customer.name if sale.customer else "Não identificado",
            "total_amount": sale.total_amount,
            "discount": sale.discount_amount,
            "final_amount": sale.final_amount,
            "payment_method": sale.payment_method,
            "payment_status": sale.payment_status,
            "items_count": len(sale.items)
        })
        total_sales += 1
        total_amount += sale.final_amount
    
    if format == "csv":
        # Gerar CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow([
            "ID", "Data", "Cliente", "Valor Total", "Desconto", 
            "Valor Final", "Método Pagamento", "Status", "Qtd Itens"
        ])
        
        # Dados
        for row in report_data:
            writer.writerow([
                row["id"], row["date"], row["customer"], row["total_amount"],
                row["discount"], row["final_amount"], row["payment_method"],
                row["payment_status"], row["items_count"]
            ])
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=sales_report.csv"}
        )
    
    return {
        "period": {
            "start_date": start_date.strftime("%d/%m/%Y") if start_date else None,
            "end_date": end_date.strftime("%d/%m/%Y") if end_date else None
        },
        "summary": {
            "total_sales": total_sales,
            "total_amount": total_amount,
            "average_sale": total_amount / total_sales if total_sales > 0 else 0
        },
        "sales": report_data
    }

@router.get("/products/top-selling")
async def top_selling_products(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Produtos mais vendidos"""
    query = db.query(
        Product.id,
        Product.name,
        Product.price,
        func.sum(SaleItem.quantity).label("total_quantity"),
        func.sum(SaleItem.total_price).label("total_revenue")
    ).join(SaleItem, Product.id == SaleItem.product_id)\
     .join(Sale, SaleItem.sale_id == Sale.id)
    
    if start_date:
        query = query.filter(func.date(Sale.created_at) >= start_date)
    else:
        query = query.filter(Sale.created_at >= datetime.now() - timedelta(days=30))
    
    if end_date:
        query = query.filter(func.date(Sale.created_at) <= end_date)
    
    query = query.group_by(Product.id, Product.name, Product.price)\
                .order_by(desc("total_quantity"))\
                .limit(limit)
    
    results = query.all()
    
    return [
        {
            "product_id": result.id,
            "product_name": result.name,
            "unit_price": result.price,
            "total_quantity": result.total_quantity,
            "total_revenue": result.total_revenue
        }
        for result in results
    ]

@router.get("/inventory/low-stock")
async def low_stock_report(db: Session = Depends(get_db)):
    """Relatório de produtos com estoque baixo"""
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
            "max_stock": inv.max_stock,
            "location": inv.location,
            "status": "CRÍTICO" if inv.quantity == 0 else "BAIXO"
        }
        for inv in low_stock
    ]

@router.get("/financial/daily")
async def daily_financial_report(
    report_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Relatório financeiro diário"""
    if not report_date:
        report_date = date.today()
    
    # Vendas do dia
    sales_today = db.query(Sale).filter(func.date(Sale.created_at) == report_date).all()
    
    total_sales = len(sales_today)
    total_revenue = sum(sale.final_amount for sale in sales_today)
    total_discounts = sum(sale.discount_amount for sale in sales_today)
    
    # Pagamentos por método
    payments_by_method = {}
    for sale in sales_today:
        method = sale.payment_method
        if method not in payments_by_method:
            payments_by_method[method] = {"count": 0, "amount": 0}
        payments_by_method[method]["count"] += 1
        payments_by_method[method]["amount"] += sale.final_amount
    
    # Vendas por hora
    hourly_sales = {}
    for sale in sales_today:
        hour = sale.created_at.hour
        if hour not in hourly_sales:
            hourly_sales[hour] = {"count": 0, "amount": 0}
        hourly_sales[hour]["count"] += 1
        hourly_sales[hour]["amount"] += sale.final_amount
    
    return {
        "date": report_date.strftime("%d/%m/%Y"),
        "summary": {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_discounts": total_discounts,
            "average_sale": total_revenue / total_sales if total_sales > 0 else 0
        },
        "payment_methods": payments_by_method,
        "hourly_sales": hourly_sales
    }

@router.get("/customers/top")
async def top_customers(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Clientes que mais compram"""
    query = db.query(
        Customer.id,
        Customer.name,
        Customer.email,
        func.count(Sale.id).label("total_purchases"),
        func.sum(Sale.final_amount).label("total_spent")
    ).join(Sale, Customer.id == Sale.customer_id)
    
    if start_date:
        query = query.filter(func.date(Sale.created_at) >= start_date)
    else:
        query = query.filter(Sale.created_at >= datetime.now() - timedelta(days=30))
    
    if end_date:
        query = query.filter(func.date(Sale.created_at) <= end_date)
    
    query = query.group_by(Customer.id, Customer.name, Customer.email)\
                .order_by(desc("total_spent"))\
                .limit(limit)
    
    results = query.all()
    
    return [
        {
            "customer_id": result.id,
            "customer_name": result.name,
            "customer_email": result.email,
            "total_purchases": result.total_purchases,
            "total_spent": result.total_spent,
            "average_purchase": result.total_spent / result.total_purchases if result.total_purchases > 0 else 0
        }
        for result in results
    ]

@router.get("/dashboard/summary")
async def dashboard_summary(db: Session = Depends(get_db)):
    """Resumo para dashboard"""
    today = date.today()
    
    # Vendas de hoje
    sales_today = db.query(Sale).filter(func.date(Sale.created_at) == today).count()
    revenue_today = db.query(func.sum(Sale.final_amount)).filter(
        func.date(Sale.created_at) == today
    ).scalar() or 0
    
    # Vendas do mês
    month_start = today.replace(day=1)
    sales_month = db.query(Sale).filter(Sale.created_at >= month_start).count()
    revenue_month = db.query(func.sum(Sale.final_amount)).filter(
        Sale.created_at >= month_start
    ).scalar() or 0
    
    # Produtos com estoque baixo
    low_stock_count = db.query(Inventory).filter(
        Inventory.quantity <= Inventory.min_stock
    ).count()
    
    # Total de produtos ativos
    total_products = db.query(Product).filter(Product.active == True).count()
    
    # Total de clientes ativos
    total_customers = db.query(Customer).filter(Customer.active == True).count()
    
    return {
        "today": {
            "sales": sales_today,
            "revenue": revenue_today
        },
        "month": {
            "sales": sales_month,
            "revenue": revenue_month
        },
        "inventory": {
            "low_stock_count": low_stock_count,
            "total_products": total_products
        },
        "customers": {
            "total_active": total_customers
        }
    }
