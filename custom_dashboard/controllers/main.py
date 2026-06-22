# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime

class EcommerceDashboardController(http.Controller):

    @http.route('/custom_dashboard/get_kpis', type='json', auth='user', methods=['POST'])
    def get_dashboard_kpis(self, date_filter='all', partner_id=None, **kwargs):
        # 1. Filtros base por fecha y estado de la orden
        domain = [('state', 'in', ['sale', 'done'])]
        cart_domain = [('state', '=', 'draft'), ('cart_quantity', '>', 0)]
        
        today = datetime.now()
        if date_filter == 'today':
            date_str = today.strftime('%Y-%m-%d 00:00:00')
            domain.append(('date_order', '>=', date_str))
            cart_domain.append(('create_date', '>=', date_str))
        elif date_filter == 'this_month':
            date_str = today.replace(day=1).strftime('%Y-%m-%d 00:00:00')
            domain.append(('date_order', '>=', date_str))
            cart_domain.append(('create_date', '>=', date_str))
        elif date_filter == 'this_year':
            domain.append(('date_order', '>=', f"{today.year}-01-01 00:00:00"))
            cart_domain.append(('create_date', '>=', f"{today.year}-01-01 00:00:00"))

        if partner_id:
            domain.append(('partner_id', '=', int(partner_id)))

        # 2. Consultas y Totales Financieros
        orders = request.env['sale.order'].search(domain)
        total_sales = sum(orders.mapped('amount_total'))
        orders_count = len(orders)
        average_ticket = total_sales / orders_count if orders_count > 0 else 0.0

        # --- NUEVAS METRICAS FINANCIERAS ---
        # Buscamos las notas de crédito (devoluciones) validadas en el mismo rango de fecha
        invoice_domain = [('move_type', '=', 'out_refund'), ('state', '=', 'posted')]
        
        if date_filter == 'today':
            invoice_domain.append(('invoice_date', '=', today.strftime('%Y-%m-%d')))
        elif date_filter == 'this_month':
            invoice_domain.append(('invoice_date', '>=', today.replace(day=1).strftime('%Y-%m-%d')))
        elif date_filter == 'this_year':
            invoice_domain.append(('invoice_date', '>=', f"{today.year}-01-01"))

        if partner_id:
            invoice_domain.append(('partner_id', '=', int(partner_id)))

        refund_invoices = request.env['account.move'].search(invoice_domain)
        total_refunds = sum(refund_invoices.mapped('amount_total'))
        
        # Ventas Netas = Ingresos Brutos - Devoluciones
        net_sales = total_sales - total_refunds

        # 3. Gestión de Carritos y Tasa de Conversión (Marketing Avanzado)
        abandoned_carts = request.env['sale.order'].search(cart_domain)
        abandoned_carts_count = len(abandoned_carts)
        
        # Calculamos el dinero total estancado en los carritos abandonados
        total_abandoned_revenue = sum(abandoned_carts.mapped('amount_total'))

        total_attempts = orders_count + abandoned_carts_count
        conversion_rate = (orders_count / total_attempts * 100) if total_attempts > 0 else 0.0

        # --- NUEVA METRICA: Tasa de Recurrencia de Clientes ---
        # Contamos cuántos clientes únicos han comprado en este periodo y cuántos repitieron
        if orders:
            partner_ids = orders.mapped('partner_id.id')
            # Contamos cuántas órdenes tiene cada cliente en el universo actual filtrado
            from collections import Counter
            order_counts_per_partner = Counter(partner_ids)
            
            unique_customers = len(order_counts_per_partner)
            repeat_customers = sum(1 for partner, count in order_counts_per_partner.items() if count > 1)
            
            recurrence_rate = (repeat_customers / unique_customers * 100) if unique_customers > 0 else 0.0
        else:
            recurrence_rate = 0.0

        # 4. Operaciones y Logística (Despachos pendientes)
        pending_delivery = request.env['sale.order'].search_count([
            ('state', 'in', ['sale', 'done']),
            ('delivery_status', 'in', ['pending', 'started'])
        ])

        # 5. Control de Inventario Crítico (Variantes con stock cero o menos)
        low_stock_products = request.env['product.product'].search([
            ('sale_ok', '=', True),
            ('qty_available', '<=', 0),
            ('detailed_type', '=', 'product')
        ])
        low_stock_count = len(low_stock_products)
        low_stock_ids = low_stock_products.ids  # <-- Guardamos los IDs para el clic

        # Aprovechamos para sacar también los IDs de órdenes con despachos pendientes
        pending_delivery_orders = request.env['sale.order'].search([
            ('state', 'in', ['sale', 'done']),
            ('delivery_status', 'in', ['pending', 'started'])
        ])
        pending_delivery_count = len(pending_delivery_orders)
        pending_delivery_ids = pending_delivery_orders.ids

        # 6. Listado de clientes para el selector de filtros en el Frontend
        partners = request.env['res.partner'].search([('customer_rank', '>', 0)], limit=30)
        partner_list = [{'id': p.id, 'name': p.name} for p in partners]

        # 7. Inicialización de listas para las dimensiones analíticas
        top_products = []
        top_customers = []
        shipping_methods = []
        sales_channels = []

        # Solo ejecutamos las consultas complejas si existen órdenes en el filtro actual
        if orders:
            order_ids = tuple(orders.ids) if len(orders.ids) > 1 else (orders.ids[0],)

            # SQL: Top 5 Productos Estrellas
            request.env.cr.execute("""
                SELECT sol.product_id, pt.name as product_name, SUM(sol.product_uom_qty) as total_qty, SUM(sol.price_subtotal) as total_amount
                FROM sale_order_line sol
                JOIN product_product pp ON sol.product_id = pp.id
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE sol.order_id IN %s
                GROUP BY sol.product_id, pt.name
                ORDER BY total_qty DESC LIMIT 5
            """, (order_ids,))
            
            for row in request.env.cr.dictfetchall():
                p_name = row['product_name']
                if isinstance(p_name, dict):
                    p_name = p_name.get('es_DO') or p_name.get('en_US') or list(p_name.values())[0]
                
                top_products.append({
                    'id': row['product_id'],
                    'name': str(p_name),
                    'qty': int(row['total_qty']),
                    'amount': float(row['total_amount'])
                })

            # SQL: Top 5 Clientes VIP
            request.env.cr.execute("""
                SELECT so.partner_id, rp.name as customer_name, COUNT(so.id) as order_qty, SUM(so.amount_total) as total_spent
                FROM sale_order so
                JOIN res_partner rp ON so.partner_id = rp.id
                WHERE so.id IN %s
                GROUP BY so.partner_id, rp.name
                ORDER BY total_spent DESC LIMIT 5
            """, (order_ids,))
            
            for row in request.env.cr.dictfetchall():
                top_customers.append({
                    'id': row['partner_id'],
                    'name': row['customer_name'],
                    'qty': int(row['order_qty']),
                    'spent': float(row['total_spent'])
                })

            # SQL: Métodos de Envío más Utilizados
            request.env.cr.execute("""
                SELECT so.carrier_id, pc.name as carrier_name, COUNT(so.id) as total_orders
                FROM sale_order so
                JOIN delivery_carrier dc ON so.carrier_id = dc.id
                JOIN product_template pc ON dc.product_id = pc.id
                WHERE so.id IN %s
                GROUP BY so.carrier_id, pc.name
                ORDER BY total_orders DESC LIMIT 3
            """, (order_ids,))
            
            for row in request.env.cr.dictfetchall():
                carrier_name = row['carrier_name']
                if isinstance(carrier_name, dict):
                    carrier_name = carrier_name.get('es_DO') or carrier_name.get('en_US') or list(carrier_name.values())[0]
                
                shipping_methods.append({
                    'name': str(carrier_name),
                    'count': row['total_orders']
                })

            # SQL: Rendimiento por Canal / Equipos de Venta con Porcentaje Dinámico
            request.env.cr.execute("""
                SELECT so.team_id, st.name as team_name, SUM(so.amount_total) as total_revenue
                FROM sale_order so
                JOIN crm_team st ON so.team_id = st.id
                WHERE so.id IN %s
                GROUP BY so.team_id, st.name
                ORDER BY total_revenue DESC
            """, (order_ids,))
            
            for row in request.env.cr.dictfetchall():
                team_name = row['team_name']
                if isinstance(team_name, dict):
                    team_name = team_name.get('es_DO') or team_name.get('en_US') or list(team_name.values())[0]
                
                revenue = float(row['total_revenue'])
                percentage = (revenue / total_sales * 100) if total_sales > 0 else 0.0

                sales_channels.append({
                    'name': str(team_name),
                    'revenue': revenue,
                    'percentage': percentage
                })

        return {
            'total_sales': total_sales,
            'orders_count': orders_count,
            'average_ticket': average_ticket,
            'total_refunds': total_refunds,  # <-- Agregado
            'net_sales': net_sales,          # <-- Agregado
            'refund_ids': refund_invoices.ids,          # <-- Agregado
            'order_ids': orders.ids,                    # <-- Agregado
            'pending_delivery': pending_delivery,
            'pending_delivery_ids': pending_delivery_ids,  # <-- Agregado
            'conversion_rate': conversion_rate,
            'abandoned_carts': abandoned_carts_count,
            'abandoned_ids': abandoned_carts.ids,        # <-- Agregado
            'total_abandoned_revenue': total_abandoned_revenue,  # <-- Agregado
            'recurrence_rate': recurrence_rate,                  # <-- Agregado
            'low_stock_count': low_stock_count,
            'low_stock_ids': low_stock_ids,                # <-- Agregado
            'top_products': top_products,
            'top_customers': top_customers,
            'shipping_methods': shipping_methods,
            'sales_channels': sales_channels,
            'partners_available': partner_list
        }