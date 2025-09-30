from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from pathlib import Path

# Importar modelos para criar as tabelas
from backend.models.product import Product, Category
from backend.models.customer import Customer
from backend.models.sale import Sale, SaleItem
from backend.models.inventory import Inventory, InventoryMovement
from backend.models.payment import PaymentMethod, Payment
from backend.database import create_tables, get_db

# Importar routers
from backend.routers import products, customers, sales, inventory, payments, reports

# Criar instância do FastAPI
app = FastAPI(
    title="Sistema_PDV",
    description="Sistema de Ponto de Venda completo",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(sales.router, prefix="/api/sales", tags=["sales"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

# Servir arquivos estáticos
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

@app.on_event("startup")
async def startup_event():
    """Criar tabelas do banco de dados na inicialização"""
    create_tables()
    print("✅ Banco de dados inicializado!")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Página inicial do sistema"""
    frontend_file = Path(__file__).parent / "frontend" / "templates" / "index.html"
    if frontend_file.exists():
        return HTMLResponse(content=frontend_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="""
    <html>
        <head><title>Sistema_PDV</title></head>
        <body>
            <h1>Sistema_PDV - Sistema de Ponto de Venda</h1>
            <p>API funcionando! Acesse <a href="/docs">/docs</a> para ver a documentação.</p>
        </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    return {"status": "healthy", "message": "Projeto_PDV está funcionando!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
