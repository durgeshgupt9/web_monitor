{
    'name': 'Website Monitor',
    'version': '17.0.1.0.0',  # If your module is for Odoo 17.0
    'category': 'Tools',
    'summary': 'Monitor website URL and port, email alerts, manual check, status in header',
    'author': 'Odoo Community Association (OCA)',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/monitor_views.xml',
        'data/monitor_cron.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
