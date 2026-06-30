# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    activo_custom = fields.Boolean(
        string='Activo',
        default=False,
        help='Campo personalizado de Cecomsa. No tiene relación con el campo '
             'nativo "Active" de Odoo (que controla el archivado del producto).',
    )
