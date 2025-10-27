# -*- coding: utf-8 -*-
{
    'name': "Student_Visa_Consultancy_Management",

    'summary': "Short",

    'description': """
Long description of module's purpose
    """,

    'author': "nishat",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','website',],

    # always loaded
    'data': [
        'security/security.xml',
         'security/ir.model.access.csv',
        'data/secquence.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/student.xml',
        'views/university.xml',
        'views/application.xml',
        'views/document.xml',
        'views/payment.xml',
        'views/consaltant.xml',
        'views/crouse.xml',
        'views/invoice.xml',
        'views/invoice_report.xml',
        'views/dashboard.xml',
        'views/portal.xml',
        'views/sidebar.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

}

