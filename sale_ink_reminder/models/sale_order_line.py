from odoo import models, fields, api
from datetime import datetime, timedelta

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Campo de control para evitar duplicados
    ink_reminder_sent = fields.Boolean(
        string='Recordatorio de tinta enviado', 
        default=False, 
        copy=False
    )

    @api.model
    def _cron_send_ink_reminders(self):
        """Método que ejecuta el Cron para buscar ventas de impresoras de hace 45 días"""
        target_date = datetime.now().date() - timedelta(days=0)
        
        lines_to_remind = self.search([
            ('order_id.state', 'in', ['sale', 'done']),
            ('product_id.categ_id.name', '=', 'Impresoras'),
            ('order_id.date_order', '>=', datetime.combine(target_date, datetime.min.time())),
            ('order_id.date_order', '<=', datetime.combine(target_date, datetime.max.time())),
            ('ink_reminder_sent', '=', False)
        ])

        template = self.env.ref('sale_ink_reminder.email_template_ink_reminder', raise_if_not_found=False)
        if not template:
            return

        for line in lines_to_remind:
            if line.order_id.partner_id.email and line.product_id.accessory_product_ids:
                template.send_mail(line.id, force_send=True)
                line.ink_reminder_sent = True