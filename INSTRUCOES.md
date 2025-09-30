# 🐆 Sistema_PDV - Sistema de Ponto de Venda

## ✅ Sistema Criado com Sucesso!

O **Sistema_PDV** foi desenvolvido com todas as funcionalidades solicitadas:

### 🚀 Funcionalidades Implementadas

#### 1. **Processamento de Vendas**
- ✅ Registro de itens com quantidade e preços
- ✅ Cálculo automático de totais e descontos
- ✅ Geração de recibos de venda
- ✅ Suporte a múltiplos itens por venda

#### 2. **Controle de Estoque**
- ✅ Atualização automática do estoque a cada venda
- ✅ Prevenção de vendas de produtos indisponíveis
- ✅ Alertas de estoque baixo
- ✅ Histórico de movimentações de estoque

#### 3. **Gestão Financeira e NFC-e**
- ✅ Estrutura preparada para emissão de NFC-e
- ✅ Controle de status de pagamento
- ✅ Integração com dados de vendas
- ✅ Relatórios financeiros

#### 4. **Gestão de Formas de Pagamento**
- ✅ Dinheiro
- ✅ Cartão de Débito
- ✅ Cartão de Crédito
- ✅ PIX
- ✅ Vale Alimentação
- ✅ Cálculo automático de taxas

#### 5. **Cadastro e Gestão de Clientes**
- ✅ Registro completo de informações
- ✅ Histórico de compras
- ✅ Busca por CPF/CNPJ e email
- ✅ Endereços completos

#### 6. **Relatórios e Análise de Desempenho**
- ✅ Dashboard com estatísticas em tempo real
- ✅ Relatório de vendas
- ✅ Produtos mais vendidos
- ✅ Análise de estoque
- ✅ Relatórios por período
- ✅ Exportação de dados

### 🎨 Design e Interface

- ✅ **Cores**: #00df81 (verde principal), #ededed (fundo), #021b1b (detalhes)
- ✅ Interface moderna e responsiva
- ✅ Navegação intuitiva
- ✅ Modais para cadastros
- ✅ Tabelas interativas
- ✅ Alertas e notificações

### 🛠️ Tecnologias Utilizadas

#### Backend
- **Python 3.13** com FastAPI
- **SQLAlchemy** para ORM
- **SQLite** como banco de dados
- **Pydantic** para validação de dados
- **Uvicorn** como servidor ASGI

#### Frontend
- **HTML5** semântico
- **CSS3** com variáveis CSS e Flexbox/Grid
- **JavaScript** vanilla (ES6+)
- **Design responsivo**

### 📁 Estrutura do Projeto

```
Projeto_PDV/
├── backend/
│   ├── models/          # Modelos do banco de dados
│   ├── routers/         # APIs REST
│   ├── database.py      # Configuração do banco
│   ├── schemas.py       # Schemas Pydantic
│   └── init_data.py     # Dados de exemplo
├── frontend/
│   ├── static/
│   │   ├── css/         # Estilos
│   │   └── js/          # JavaScript
│   └── templates/       # Templates HTML
├── main.py              # Aplicação principal
├── run.py               # Script de execução
├── setup.py             # Script de configuração
└── requirements.txt     # Dependências
```

## 🚀 Como Executar

### 1. **Primeira Execução (Configuração)**
```bash
cd /home/lexi/Downloads/PROJETOS/Projeto_PDV

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados
PYTHONPATH=/home/lexi/Downloads/PROJETOS/Projeto_PDV python backend/init_data.py
```

### 2. **Executar o Sistema**
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar servidor
PYTHONPATH=/home/lexi/Downloads/PROJETOS/Projeto_PDV python run.py
```

### 3. **Acessar o Sistema**
- **Interface Web**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 📊 Dados de Exemplo Incluídos

O sistema já vem com dados de exemplo:

### Produtos (8 itens)
- Smartphone Samsung Galaxy A54
- Notebook Dell Inspiron 15
- Camiseta Polo Masculina
- Arroz 5kg
- Livro Python para Iniciantes
- Mesa de Centro
- Fone de Ouvido Bluetooth
- Calça Jeans Feminina

### Clientes (4 clientes)
- João Silva
- Maria Santos
- Pedro Oliveira
- Ana Costa

### Métodos de Pagamento (5 tipos)
- Dinheiro
- Cartão de Débito
- Cartão de Crédito
- PIX
- Vale Alimentação

## 🔧 APIs Disponíveis

### Produtos
- `GET /api/products/` - Listar produtos
- `POST /api/products/` - Criar produto
- `GET /api/products/{id}` - Obter produto
- `PUT /api/products/{id}` - Atualizar produto
- `DELETE /api/products/{id}` - Excluir produto

### Clientes
- `GET /api/customers/` - Listar clientes
- `POST /api/customers/` - Criar cliente
- `GET /api/customers/{id}` - Obter cliente
- `PUT /api/customers/{id}` - Atualizar cliente
- `DELETE /api/customers/{id}` - Excluir cliente

### Vendas
- `GET /api/sales/` - Listar vendas
- `POST /api/sales/` - Criar venda
- `GET /api/sales/{id}` - Obter venda
- `GET /api/sales/{id}/receipt` - Gerar recibo

### Estoque
- `GET /api/inventory/` - Listar estoque
- `POST /api/inventory/` - Criar/atualizar estoque
- `POST /api/inventory/adjust/{product_id}` - Ajustar estoque

### Relatórios
- `GET /api/reports/sales` - Relatório de vendas
- `GET /api/reports/products/top-selling` - Produtos mais vendidos
- `GET /api/reports/inventory/low-stock` - Produtos com estoque baixo
- `GET /api/reports/dashboard/summary` - Resumo do dashboard

## 🎯 Próximos Passos Sugeridos

1. **Personalização**: Ajustar cores e layout conforme necessário
2. **NFC-e**: Integrar com provedor de NFC-e (ex: NFe.io, SEFAZ)
3. **Impressão**: Adicionar funcionalidade de impressão de recibos
4. **Backup**: Implementar sistema de backup automático
5. **Segurança**: Adicionar autenticação e autorização
6. **Mobile**: Criar versão mobile/PWA

## 🆘 Suporte

O sistema está pronto para uso! Todas as funcionalidades básicas de um PDV estão implementadas e funcionando.

Para dúvidas ou melhorias, consulte:
- Documentação da API: http://localhost:8000/docs
- Código fonte bem documentado
- Logs do servidor no terminal

---

**🧾 Projeto_PDV - Sistema completo de Ponto de Venda desenvolvido em Python!**
