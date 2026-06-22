/** @odoo-module */

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class EcommerceDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.actionService = useService("action");
        
        this.state = useState({
            activeTab: 'financial',
            filters: {
                date: 'all',
                partner: ''
            },
            kpis: {
                total_sales: 0,
                orders_count: 0,
                average_ticket: 0,
                total_refunds: 0,
                net_sales: 0,
                pending_delivery: 0,
                pending_delivery_ids: [],
                conversion_rate: 0,
                abandoned_carts: 0,
                total_abandoned_revenue: 0,
                recurrence_rate: 0,
                low_stock_count: 0,
                low_stock_ids: [],
                top_products: [],
                top_customers: [],
                shipping_methods: [],
                sales_channels: [],
                partners_available: []
            }
        });

        // CORRECCIÓN: Usamos la función de flecha manteniendo explícito el contexto de 'this'
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    // Aseguramos que la función exista dentro de la estructura de la clase
    async loadDashboardData() {
        try {
            const result = await this.rpc("/custom_dashboard/get_kpis", {
                date_filter: this.state.filters.date,
                partner_id: this.state.filters.partner ? parseInt(this.state.filters.partner) : null
            });
            if (result) {
                this.state.kpis = result;
            }
        } catch (error) {
            console.error("Error al actualizar la suite de BI:", error);
        }
    }

    changeTab(tabName) {
        this.state.activeTab = tabName;
    }

    async onDateFilterChange(ev) {
        this.state.filters.date = ev.target.value;
        await this.loadDashboardData();
    }

    async onPartnerFilterChange(ev) {
        this.state.filters.partner = ev.target.value;
        await this.loadDashboardData();
    }

    openLowStockAction() {
        if (!this.state.kpis.low_stock_ids.length) return;
        
        this.actionService.doAction({
            name: "Productos en Quiebre de Stock (Abastecer)",
            type: "ir.actions.act_window",
            res_model: "product.product",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [['id', 'in', this.state.kpis.low_stock_ids]],
            target: "current",
        });
    }

    openPendingDeliveriesAction() {
        if (!this.state.kpis.pending_delivery_ids.length) return;

        this.actionService.doAction({
            name: "Órdenes con Despachos Pendientes",
            type: "ir.actions.act_window",
            res_model: "sale.order",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [['id', 'in', this.state.kpis.pending_delivery_ids]],
            context: { create: false },
            target: "current",
        });
    }

    // ... (Mantén tu setup y funciones anteriores iguales)

    // ACCIÓN: Abre las Órdenes de Venta Facturadas
    openOrdersAction() {
        if (!this.state.kpis.order_ids.length) return;
        this.actionService.doAction({
            name: "Órdenes de Venta Confirmadas",
            type: "ir.actions.act_window",
            res_model: "sale.order",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [['id', 'in', this.state.kpis.order_ids]],
            target: "current",
        });
    }

    // ACCIÓN: Abre las Notas de Crédito / Devoluciones
    openRefundsAction() {
        if (!this.state.kpis.refund_ids.length) return;
        this.actionService.doAction({
            name: "Notas de Crédito / Devoluciones",
            type: "ir.actions.act_window",
            res_model: "account.move",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [['id', 'in', this.state.kpis.refund_ids]],
            target: "current",
        });
    }

    // ACCIÓN: Abre los Carritos Abandonados
    openAbandonedCartsAction() {
        if (!this.state.kpis.abandoned_ids.length) return;
        this.actionService.doAction({
            name: "Carritos Abandonados",
            type: "ir.actions.act_window",
            res_model: "sale.order",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [['id', 'in', this.state.kpis.abandoned_ids]],
            target: "current",
        });
    }
}

EcommerceDashboard.template = "custom_dashboard.EcommerceDashboardView";
registry.category("actions").add("custom_dashboard.ecommerce_dashboard", EcommerceDashboard);