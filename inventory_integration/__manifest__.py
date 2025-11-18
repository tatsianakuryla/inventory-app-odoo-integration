{
    'name': 'Inventory Integration',
    'version': '1.0.0',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_field_views.xml',
        'views/inventory_import_views.xml',
        'wizard/import_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
