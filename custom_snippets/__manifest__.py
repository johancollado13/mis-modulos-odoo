# -*- coding: utf-8 -*-
{
    'name': 'Mis Snippets Personalizados',
    'summary': 'Snippets a medida para el editor web de Odoo 17',
    'category': 'Website',
    'version': '17.0.1.0.2',  # Subimos la versión para forzar a Odoo a leerlo de cero
    'depends': ['base', 'website'],
    'data': [
        'views/snippets.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}