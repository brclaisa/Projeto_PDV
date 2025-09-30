// Projeto_PDV - JavaScript Principal

class PantherPDV {
    constructor() {
        this.currentSection = 'dashboard';
        this.apiBase = '/api';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.initializePaymentMethods();
    }

    setupEventListeners() {
        // Navegação
        document.querySelectorAll('.nav-menu a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                this.showSection(section);
            });
        });

        // Modais
        document.querySelectorAll('.modal .close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal'));
            });
        });

        // Fechar modal clicando fora
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });

        // Formulários
        this.setupFormHandlers();
    }

    setupFormHandlers() {
        // Formulário de produtos
        const productForm = document.getElementById('productForm');
        if (productForm) {
            productForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleProductSubmit(e);
            });
        }

        // Formulário de clientes
        const customerForm = document.getElementById('customerForm');
        if (customerForm) {
            customerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleCustomerSubmit(e);
            });
        }

        // Formulário de vendas
        const saleForm = document.getElementById('saleForm');
        if (saleForm) {
            saleForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSaleSubmit(e);
            });
        }
    }

    showSection(section) {
        // Atualizar navegação ativa
        document.querySelectorAll('.nav-menu a').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Esconder todas as seções
        document.querySelectorAll('.section').forEach(sec => {
            sec.style.display = 'none';
        });

        // Mostrar seção selecionada
        const targetSection = document.getElementById(section);
        if (targetSection) {
            targetSection.style.display = 'block';
            this.currentSection = section;

            // Carregar dados específicos da seção
            this.loadSectionData(section);
        }
    }

    async loadSectionData(section) {
        switch (section) {
            case 'dashboard':
                await this.loadDashboard();
                break;
            case 'products':
                await this.loadProducts();
                break;
            case 'customers':
                await this.loadCustomers();
                break;
            case 'sales':
                await this.loadSales();
                break;
            case 'inventory':
                await this.loadInventory();
                break;
            case 'reports':
                await this.loadReports();
                break;
        }
    }

    async loadDashboard() {
        try {
            const response = await fetch(`${this.apiBase}/reports/dashboard/summary`);
            const data = await response.json();

            this.updateDashboardStats(data);
            await this.loadTodaySales();
        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
            this.showAlert('Erro ao carregar dados do dashboard', 'danger');
        }
    }

    updateDashboardStats(data) {
        const stats = {
            'sales-today': data.today.sales,
            'revenue-today': this.formatCurrency(data.today.revenue),
            'sales-month': data.month.sales,
            'revenue-month': this.formatCurrency(data.month.revenue),
            'low-stock': data.inventory.low_stock_count,
            'total-products': data.inventory.total_products,
            'total-customers': data.customers.total_active
        };

        Object.entries(stats).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    async loadTodaySales() {
        try {
            const response = await fetch(`${this.apiBase}/sales/today/summary`);
            const data = await response.json();

            this.updateTodaySalesChart(data);
        } catch (error) {
            console.error('Erro ao carregar vendas do dia:', error);
        }
    }

    updateTodaySalesChart(data) {
        const chartContainer = document.getElementById('todaySalesChart');
        if (!chartContainer) return;

        const methods = Object.keys(data.payment_methods);
        const amounts = Object.values(data.payment_methods).map(m => m.amount);

        // Criar gráfico simples (pode ser substituído por uma biblioteca como Chart.js)
        chartContainer.innerHTML = `
            <div class="payment-methods-chart">
                ${methods.map((method, index) => `
                    <div class="payment-method-item">
                        <span class="method-name">${method}</span>
                        <span class="method-amount">${this.formatCurrency(amounts[index])}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    async loadProducts() {
        try {
            const response = await fetch(`${this.apiBase}/products/`);
            const products = await response.json();

            this.renderProductsTable(products);
        } catch (error) {
            console.error('Erro ao carregar produtos:', error);
            this.showAlert('Erro ao carregar produtos', 'danger');
        }
    }

    renderProductsTable(products) {
        const tbody = document.querySelector('#productsTable tbody');
        if (!tbody) return;

        tbody.innerHTML = products.map(product => `
            <tr>
                <td>${product.id}</td>
                <td>${product.name}</td>
                <td>${product.barcode || '-'}</td>
                <td>${product.category || '-'}</td>
                <td>${this.formatCurrency(product.price)}</td>
                <td>
                    <span class="status-${product.active ? 'active' : 'inactive'}">
                        ${product.active ? 'Ativo' : 'Inativo'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="pantherPDV.editProduct(${product.id})">
                        Editar
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="pantherPDV.deleteProduct(${product.id})">
                        Excluir
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadCustomers() {
        try {
            const response = await fetch(`${this.apiBase}/customers/`);
            const customers = await response.json();

            this.renderCustomersTable(customers);
        } catch (error) {
            console.error('Erro ao carregar clientes:', error);
            this.showAlert('Erro ao carregar clientes', 'danger');
        }
    }

    renderCustomersTable(customers) {
        const tbody = document.querySelector('#customersTable tbody');
        if (!tbody) return;

        tbody.innerHTML = customers.map(customer => `
            <tr>
                <td>${customer.id}</td>
                <td>${customer.name}</td>
                <td>${customer.email || '-'}</td>
                <td>${customer.phone || '-'}</td>
                <td>${customer.document || '-'}</td>
                <td>
                    <span class="status-${customer.active ? 'active' : 'inactive'}">
                        ${customer.active ? 'Ativo' : 'Inativo'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="pantherPDV.editCustomer(${customer.id})">
                        Editar
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="pantherPDV.deleteCustomer(${customer.id})">
                        Excluir
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadSales() {
        try {
            const response = await fetch(`${this.apiBase}/sales/`);
            const sales = await response.json();

            this.renderSalesTable(sales);
        } catch (error) {
            console.error('Erro ao carregar vendas:', error);
            this.showAlert('Erro ao carregar vendas', 'danger');
        }
    }

    renderSalesTable(sales) {
        const tbody = document.querySelector('#salesTable tbody');
        if (!tbody) return;

        tbody.innerHTML = sales.map(sale => `
            <tr>
                <td>${sale.id}</td>
                <td>${this.formatDateTime(sale.created_at)}</td>
                <td>${sale.customer?.name || 'Não identificado'}</td>
                <td>${this.formatCurrency(sale.total_amount)}</td>
                <td>${this.formatCurrency(sale.discount_amount)}</td>
                <td>${this.formatCurrency(sale.final_amount)}</td>
                <td>${sale.payment_method}</td>
                <td>
                    <span class="status-${sale.payment_status}">
                        ${this.getPaymentStatusText(sale.payment_status)}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="pantherPDV.viewSaleReceipt(${sale.id})">
                        Recibo
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadInventory() {
        try {
            const response = await fetch(`${this.apiBase}/inventory/`);
            const inventory = await response.json();

            this.renderInventoryTable(inventory);
        } catch (error) {
            console.error('Erro ao carregar estoque:', error);
            this.showAlert('Erro ao carregar estoque', 'danger');
        }
    }

    renderInventoryTable(inventory) {
        const tbody = document.querySelector('#inventoryTable tbody');
        if (!tbody) return;

        tbody.innerHTML = inventory.map(item => `
            <tr>
                <td>${item.product_id}</td>
                <td>${item.product?.name || 'Produto não encontrado'}</td>
                <td>${item.quantity}</td>
                <td>${item.min_stock}</td>
                <td>${item.max_stock || '-'}</td>
                <td>${item.location || '-'}</td>
                <td>
                    ${item.quantity <= item.min_stock ? 
                        '<span class="status-danger">Estoque Baixo</span>' : 
                        '<span class="status-active">Normal</span>'
                    }
                </td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="pantherPDV.adjustInventory(${item.product_id})">
                        Ajustar
                    </button>
                </td>
            </tr>
        `).join('');
    }

    async loadReports() {
        // Carregar dados para relatórios
        try {
            const [salesReport, topProducts, lowStock] = await Promise.all([
                fetch(`${this.apiBase}/reports/sales`).then(r => r.json()),
                fetch(`${this.apiBase}/reports/products/top-selling`).then(r => r.json()),
                fetch(`${this.apiBase}/reports/inventory/low-stock`).then(r => r.json())
            ]);

            this.renderReports(salesReport, topProducts, lowStock);
        } catch (error) {
            console.error('Erro ao carregar relatórios:', error);
            this.showAlert('Erro ao carregar relatórios', 'danger');
        }
    }

    renderReports(salesReport, topProducts, lowStock) {
        // Renderizar resumo de vendas
        const salesSummary = document.getElementById('salesSummary');
        if (salesSummary) {
            salesSummary.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${salesReport.summary.total_sales}</div>
                        <div class="stat-label">Total de Vendas</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${this.formatCurrency(salesReport.summary.total_amount)}</div>
                        <div class="stat-label">Faturamento Total</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${this.formatCurrency(salesReport.summary.average_sale)}</div>
                        <div class="stat-label">Ticket Médio</div>
                    </div>
                </div>
            `;
        }

        // Renderizar produtos mais vendidos
        const topProductsContainer = document.getElementById('topProducts');
        if (topProductsContainer) {
            topProductsContainer.innerHTML = topProducts.map(product => `
                <div class="product-item">
                    <span class="product-name">${product.product_name}</span>
                    <span class="product-quantity">${product.total_quantity} unidades</span>
                    <span class="product-revenue">${this.formatCurrency(product.total_revenue)}</span>
                </div>
            `).join('');
        }

        // Renderizar produtos com estoque baixo
        const lowStockContainer = document.getElementById('lowStockProducts');
        if (lowStockContainer) {
            lowStockContainer.innerHTML = lowStock.map(item => `
                <div class="stock-item">
                    <span class="product-name">${item.product_name}</span>
                    <span class="current-quantity">${item.current_quantity}</span>
                    <span class="min-quantity">Min: ${item.min_stock}</span>
                    <span class="status-${item.status === 'CRÍTICO' ? 'danger' : 'warning'}">${item.status}</span>
                </div>
            `).join('');
        }
    }

    // Métodos de manipulação de dados
    async handleProductSubmit(event) {
        const formData = new FormData(event.target);
        const productData = Object.fromEntries(formData);

        try {
            const response = await fetch(`${this.apiBase}/products/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(productData)
            });

            if (response.ok) {
                this.showAlert('Produto criado com sucesso!', 'success');
                this.closeModal(event.target.closest('.modal'));
                this.loadProducts();
            } else {
                const error = await response.json();
                this.showAlert(`Erro: ${error.detail}`, 'danger');
            }
        } catch (error) {
            console.error('Erro ao criar produto:', error);
            this.showAlert('Erro ao criar produto', 'danger');
        }
    }

    async handleCustomerSubmit(event) {
        const formData = new FormData(event.target);
        const customerData = Object.fromEntries(formData);

        try {
            const response = await fetch(`${this.apiBase}/customers/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(customerData)
            });

            if (response.ok) {
                this.showAlert('Cliente criado com sucesso!', 'success');
                this.closeModal(event.target.closest('.modal'));
                this.loadCustomers();
            } else {
                const error = await response.json();
                this.showAlert(`Erro: ${error.detail}`, 'danger');
            }
        } catch (error) {
            console.error('Erro ao criar cliente:', error);
            this.showAlert('Erro ao criar cliente', 'danger');
        }
    }

    async handleSaleSubmit(event) {
        // Implementar lógica de venda
        this.showAlert('Funcionalidade de venda em desenvolvimento', 'info');
    }

    // Métodos auxiliares
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) return;

        const alertId = 'alert-' + Date.now();
        const alert = document.createElement('div');
        alert.id = alertId;
        alert.className = `alert alert-${type} fade-in`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="close" onclick="document.getElementById('${alertId}').remove()">&times;</button>
        `;

        alertContainer.appendChild(alert);

        // Auto-remove após 5 segundos
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                alertElement.remove();
            }
        }, 5000);
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    }

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString('pt-BR');
    }

    getPaymentStatusText(status) {
        const statusMap = {
            'pending': 'Pendente',
            'paid': 'Pago',
            'cancelled': 'Cancelado'
        };
        return statusMap[status] || status;
    }

    async initializePaymentMethods() {
        try {
            const response = await fetch(`${this.apiBase}/payments/methods/`);
            const methods = await response.json();

            const select = document.getElementById('paymentMethod');
            if (select) {
                select.innerHTML = methods.map(method => 
                    `<option value="${method.name}">${method.name}</option>`
                ).join('');
            }
        } catch (error) {
            console.error('Erro ao carregar métodos de pagamento:', error);
        }
    }

    // Métodos de edição/exclusão (simplificados)
    async editProduct(id) {
        try {
            const current = await fetch(`${this.apiBase}/products/${id}`).then(r => r.json());
            const name = prompt('Editar nome do produto:', current.name);
            if (name === null) return;
            const priceInput = prompt('Editar preço (ex.: 199.90):', String(current.price));
            if (priceInput === null) return;
            const price = parseFloat(priceInput);
            if (Number.isNaN(price) || price < 0) {
                this.showAlert('Preço inválido.', 'warning');
                return;
            }

            const response = await fetch(`${this.apiBase}/products/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, price })
            });

            if (response.ok) {
                this.showAlert('Produto atualizado com sucesso!', 'success');
                this.loadProducts();
            } else {
                const err = await response.json();
                this.showAlert(err?.detail || 'Erro ao atualizar produto', 'danger');
            }
        } catch (error) {
            console.error('Erro ao editar produto:', error);
            this.showAlert('Erro ao editar produto', 'danger');
        }
    }

    async deleteProduct(id) {
        if (confirm('Tem certeza que deseja excluir este produto?')) {
            try {
                const response = await fetch(`${this.apiBase}/products/${id}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.showAlert('Produto excluído com sucesso!', 'success');
                    this.loadProducts();
                } else {
                    this.showAlert('Erro ao excluir produto', 'danger');
                }
            } catch (error) {
                console.error('Erro ao excluir produto:', error);
                this.showAlert('Erro ao excluir produto', 'danger');
            }
        }
    }

    async editCustomer(id) {
        try {
            const current = await fetch(`${this.apiBase}/customers/${id}`).then(r => r.json());
            const name = prompt('Editar nome do cliente:', current.name);
            if (name === null) return;
            const email = prompt('Editar e-mail:', current.email || '');
            if (email === null) return;
            const phone = prompt('Editar telefone:', current.phone || '');
            if (phone === null) return;

            const response = await fetch(`${this.apiBase}/customers/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, phone })
            });

            if (response.ok) {
                this.showAlert('Cliente atualizado com sucesso!', 'success');
                this.loadCustomers();
            } else {
                const err = await response.json();
                this.showAlert(err?.detail || 'Erro ao atualizar cliente', 'danger');
            }
        } catch (error) {
            console.error('Erro ao editar cliente:', error);
            this.showAlert('Erro ao editar cliente', 'danger');
        }
    }

    async deleteCustomer(id) {
        if (confirm('Tem certeza que deseja excluir este cliente?')) {
            try {
                const response = await fetch(`${this.apiBase}/customers/${id}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.showAlert('Cliente excluído com sucesso!', 'success');
                    this.loadCustomers();
                } else {
                    this.showAlert('Erro ao excluir cliente', 'danger');
                }
            } catch (error) {
                console.error('Erro ao excluir cliente:', error);
                this.showAlert('Erro ao excluir cliente', 'danger');
            }
        }
    }

    async viewSaleReceipt(id) {
        try {
            const response = await fetch(`${this.apiBase}/sales/${id}/receipt`);
            const receipt = await response.json();

            // Mostrar recibo em modal
            const modal = document.getElementById('receiptModal');
            if (modal) {
                document.getElementById('receiptContent').innerHTML = `
                    <h3>Recibo de Venda #${receipt.sale_id}</h3>
                    <p><strong>Data:</strong> ${receipt.date}</p>
                    <p><strong>Cliente:</strong> ${receipt.customer}</p>
                    <hr>
                    <h4>Itens:</h4>
                    ${receipt.items.map(item => `
                        <p>${item.product_name} - ${item.quantity}x ${this.formatCurrency(item.unit_price)} = ${this.formatCurrency(item.total_price)}</p>
                    `).join('')}
                    <hr>
                    <p><strong>Subtotal:</strong> ${this.formatCurrency(receipt.subtotal)}</p>
                    <p><strong>Desconto:</strong> ${this.formatCurrency(receipt.discount)}</p>
                    <p><strong>Total:</strong> ${this.formatCurrency(receipt.total)}</p>
                    <p><strong>Método de Pagamento:</strong> ${receipt.payment_method}</p>
                    <p><strong>Status:</strong> ${receipt.payment_status}</p>
                `;
                this.showModal('receiptModal');
            }
        } catch (error) {
            console.error('Erro ao carregar recibo:', error);
            this.showAlert('Erro ao carregar recibo', 'danger');
        }
    }

    async adjustInventory(productId) {
        const quantityInput = prompt('Digite a nova quantidade do estoque (valor inteiro >= 0):');
        if (quantityInput === null) return;
        const quantity = parseInt(quantityInput, 10);
        if (Number.isNaN(quantity) || quantity < 0) {
            this.showAlert('Quantidade inválida. Informe um inteiro maior ou igual a 0.', 'warning');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/inventory/adjust/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    quantity,
                    reason: 'Ajuste manual'
                })
            });

            const maybeJson = await response.text();
            let payload;
            try { payload = maybeJson ? JSON.parse(maybeJson) : {}; } catch { payload = {}; }

            if (response.ok) {
                const msg = payload?.message || 'Estoque ajustado com sucesso!';
                this.showAlert(msg, 'success');
                this.loadInventory();
            } else {
                const detail = payload?.detail || 'Erro ao ajustar estoque';
                this.showAlert(detail, 'danger');
            }
        } catch (error) {
            console.error('Erro ao ajustar estoque:', error);
            this.showAlert('Erro ao ajustar estoque', 'danger');
        }
    }
}

// Inicializar aplicação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    window.pantherPDV = new PantherPDV();
});
