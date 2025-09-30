# Sistema_PDV - Sistema de Ponto de Venda

Sistema completo de PDV (Ponto de Venda) desenvolvido em Python com FastAPI para backend e interface web moderna.

## Funcionalidades

- **Processamento de Vendas**: Registro de itens, cálculo de totais, aplicação de descontos e geração de recibos
- **Controle de Estoque**: Atualização automática do estoque, prevenção de vendas de produtos indisponíveis
- **Gestão Financeira**: Emissão de NFC-e e integração de dados financeiros
- **Formas de Pagamento**: Suporte a dinheiro, cartão de débito e crédito
- **Gestão de Clientes**: Cadastro e histórico de compras
- **Relatórios**: Análise de vendas, produtos mais vendidos e performance

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o servidor:
```bash
uvicorn main:app --reload --port 8005
```

4. Acesse: http://localhost:8005

## Tecnologias

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Relatórios**: ReportLab, Pandas, OpenPyXL

## Estrutura do Projeto

```
Sistema_PDV/
├── backend/
│   ├── models/
│   ├── routers/
│   ├── database.py
│   └── main.py
├── frontend/
│   ├── static/
│   ├── templates/
│   └── assets/
├── reports/
└── requirements.txt
```
