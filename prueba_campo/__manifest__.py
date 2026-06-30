# -*- coding: utf-8 -*-
{
    'name': 'Prueba Campo - Activo Personalizado',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Agrega un campo personalizado "Activo" en el formulario de productos',
    'description': """
Agrega un campo checkbox llamado "Activo" en el formulario de Productos
(Inventario), ubicado debajo del campo Company en la pestaña General Information.
Este campo es independiente del campo nativo 'active' de Odoo (que controla el
archivado del producto); es un campo nuevo de uso libre para Cecomsa.

Cuando el campo "Activo" está marcado en un producto, se muestra un mensaje
en la página pública de ese producto en la tienda online indicando que el
producto está activo para ventas.
    """,
    'author': 'Cecomsa',
    'depends': ['product', 'stock', 'website_sale'],
    'data': [
        'views/product_views.xml',
        'views/website_sale_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
