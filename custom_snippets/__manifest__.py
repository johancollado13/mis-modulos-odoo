# -*- coding: utf-8 -*-
{
    'name': 'Mis Snippets Personalizados',
    'summary': 'Estructuras de Contador, Cinta de Anuncios y Progreso de Envío Gratis',
    'category': 'Website',
    'version': '17.0.5.0.0',
    'depends': ['base', 'website', 'website_sale'], # Añadimos website_sale porque interactúa con la tienda
    'data': [
        'views/snippets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'custom_snippets/static/src/js/free_shipping_bar.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}