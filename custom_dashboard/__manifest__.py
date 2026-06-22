# -*- coding: utf-8 -*-
{
    'name': "Dashboard de Control E-commerce",
    'summary': "Tablero interactivo con métricas clave de ventas y KPIs",
    'description': """
        Dashboard personalizado para el backend de Odoo 17 que consolida
        información de pedidos, facturación y productos top de la tienda.
    """,
    'author': "Johan Collado",
    'category': 'Customizations',
    'version': '17.0.1.0.0',
    
    # Dependemos de web (para la UI) y sale (para leer las órdenes de venta)
    'depends': ['base', 'web', 'sale'],

    # Cargaremos los archivos de la vista del menú
    'data': [
        'views/dashboard_views.xml',
    ],
    
    # Aquí registraremos los componentes de JS (Owl) y estilos más adelante
    'assets': {
        'web.assets_backend': [
            'custom_dashboard/static/src/components/**/*.js',
            'custom_dashboard/static/src/components/**/*.xml',
            'custom_dashboard/static/src/components/**/*.scss',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}