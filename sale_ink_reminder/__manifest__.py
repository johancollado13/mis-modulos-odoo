{
    'name': 'Recordatorio de Tinta Automatizado',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Envía un correo automático 45 días después de comprar una impresora.',
    'author': 'Johan Collado',
    'depends': ['sale_management', 'website_sale', 'mail'],
    'data': [
        'data/mail_template_data.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}