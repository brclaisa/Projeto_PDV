"""
Script para inicializar o banco de dados com dados de exemplo
"""

from sqlalchemy.orm import Session
from backend.database import SessionLocal, create_tables
from backend.models.product import Product, Category
from backend.models.customer import Customer
from backend.models.inventory import Inventory
from backend.models.payment import PaymentMethod

def create_sample_data():
    """Criar dados de exemplo para o sistema"""
    db = SessionLocal()
    
    try:
        # Criar categorias
        categories = [
            Category(name="Eletrônicos", description="Produtos eletrônicos"),
            Category(name="Roupas", description="Vestuário"),
            Category(name="Alimentação", description="Produtos alimentícios"),
            Category(name="Casa e Jardim", description="Produtos para casa"),
            Category(name="Livros", description="Livros e revistas"),
        ]
        
        for category in categories:
            db.add(category)
        
        db.commit()
        
        # Criar produtos
        products = [
            Product(
                name="Smartphone Samsung Galaxy A54",
                description="Smartphone Android com 128GB de armazenamento",
                price=1299.90,
                cost_price=899.90,
                barcode="7891234567890",
                category="Eletrônicos",
                brand="Samsung",
                weight=0.202,
                dimensions="158.2 x 76.7 x 8.2"
            ),
            Product(
                name="Notebook Dell Inspiron 15",
                description="Notebook Intel i5, 8GB RAM, 256GB SSD",
                price=2499.90,
                cost_price=1899.90,
                barcode="7891234567891",
                category="Eletrônicos",
                brand="Dell",
                weight=1.83,
                dimensions="358.5 x 235.0 x 19.9"
            ),
            Product(
                name="Camiseta Polo Masculina",
                description="Camiseta polo de algodão, tamanho M",
                price=89.90,
                cost_price=45.90,
                barcode="7891234567892",
                category="Roupas",
                brand="Lacoste",
                weight=0.15,
                dimensions="50 x 70"
            ),
            Product(
                name="Arroz 5kg",
                description="Arroz tipo 1, pacote de 5kg",
                price=18.90,
                cost_price=12.90,
                barcode="7891234567893",
                category="Alimentação",
                brand="Tio João",
                weight=5.0,
                dimensions="30 x 20 x 8"
            ),
            Product(
                name="Livro Python para Iniciantes",
                description="Livro sobre programação em Python",
                price=79.90,
                cost_price=45.90,
                barcode="7891234567894",
                category="Livros",
                brand="Casa do Código",
                weight=0.6,
                dimensions="23 x 16 x 2.5"
            ),
            Product(
                name="Mesa de Centro",
                description="Mesa de centro em madeira mogno",
                price=459.90,
                cost_price=299.90,
                barcode="7891234567895",
                category="Casa e Jardim",
                brand="Tok&Stok",
                weight=15.0,
                dimensions="120 x 60 x 45"
            ),
            Product(
                name="Fone de Ouvido Bluetooth",
                description="Fone sem fio com cancelamento de ruído",
                price=199.90,
                cost_price=129.90,
                barcode="7891234567896",
                category="Eletrônicos",
                brand="Sony",
                weight=0.25,
                dimensions="18 x 16 x 7"
            ),
            Product(
                name="Calça Jeans Feminina",
                description="Calça jeans skinny, tamanho 38",
                price=129.90,
                cost_price=79.90,
                barcode="7891234567897",
                category="Roupas",
                brand="Levi's",
                weight=0.4,
                dimensions="25 x 100"
            ),
        ]
        
        for product in products:
            db.add(product)
        
        db.commit()
        
        # Criar estoque para os produtos
        for i, product in enumerate(products):
            inventory = Inventory(
                product_id=product.id,
                quantity=50 + (i * 10),  # Quantidades variadas
                min_stock=10,
                max_stock=100,
                location="Estoque Principal"
            )
            db.add(inventory)
        
        db.commit()
        
        # Criar clientes de exemplo
        customers = [
            Customer(
                name="João Silva",
                email="joao.silva@email.com",
                phone="(11) 99999-1111",
                document="123.456.789-00",
                address_street="Rua das Flores, 123",
                address_neighborhood="Centro",
                address_city="São Paulo",
                address_state="SP",
                address_zipcode="01234-567",
                active=True
            ),
            Customer(
                name="Maria Santos",
                email="maria.santos@email.com",
                phone="(11) 99999-2222",
                document="987.654.321-00",
                address_street="Avenida Paulista, 456",
                address_neighborhood="Bela Vista",
                address_city="São Paulo",
                address_state="SP",
                address_zipcode="01310-100",
                active=True
            ),
            Customer(
                name="Pedro Oliveira",
                email="pedro.oliveira@email.com",
                phone="(11) 99999-3333",
                document="456.789.123-00",
                address_street="Rua Augusta, 789",
                address_neighborhood="Consolação",
                address_city="São Paulo",
                address_state="SP",
                address_zipcode="01305-000",
                active=True
            ),
            Customer(
                name="Ana Costa",
                email="ana.costa@email.com",
                phone="(11) 99999-4444",
                document="789.123.456-00",
                address_street="Rua Oscar Freire, 321",
                address_neighborhood="Jardins",
                address_city="São Paulo",
                address_state="SP",
                address_zipcode="01426-001",
                active=True
            ),
        ]
        
        for customer in customers:
            db.add(customer)
        
        db.commit()
        
        # Criar métodos de pagamento
        payment_methods = [
            PaymentMethod(
                name="Dinheiro",
                type="cash",
                requires_approval=False,
                fee_percentage=0,
                active=True
            ),
            PaymentMethod(
                name="Cartão de Débito",
                type="debit_card",
                requires_approval=False,
                fee_percentage=1.5,
                active=True
            ),
            PaymentMethod(
                name="Cartão de Crédito",
                type="credit_card",
                requires_approval=False,
                fee_percentage=3.5,
                active=True
            ),
            PaymentMethod(
                name="PIX",
                type="pix",
                requires_approval=False,
                fee_percentage=0,
                active=True
            ),
            PaymentMethod(
                name="Vale Alimentação",
                type="food_voucher",
                requires_approval=False,
                fee_percentage=2.0,
                active=True
            ),
        ]
        
        for method in payment_methods:
            db.add(method)
        
        db.commit()
        
        print("✅ Dados de exemplo criados com sucesso!")
        print(f"📦 {len(products)} produtos criados")
        print(f"👥 {len(customers)} clientes criados")
        print(f"💳 {len(payment_methods)} métodos de pagamento criados")
        print(f"📋 {len(categories)} categorias criadas")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Função principal"""
    print("🚀 Inicializando banco de dados do Projeto_PDV...")
    
    # Criar tabelas
    create_tables()
    print("✅ Tabelas criadas!")
    
    # Criar dados de exemplo
    create_sample_data()
    
    print("🎉 Inicialização concluída!")

if __name__ == "__main__":
    main()
