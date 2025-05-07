# -*- coding: utf-8 -*-
{
    'name': "ITMS",

    'summary': """
        Aplikasi PMR ITMS
    """,

    'description': """
        Aplikasi PMR ITMS untuk Management dan Ticketing Dept IT
    """,

    'author': "TIM-PMR",
    'website': "",

    'category': 'PMR IT',
    'sequence': -100,
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'mail',
        'amp_approval',
        'amp_pr',
        'purchase',
        'hr',
        'hr_expense',
        'hr_recruitment',
        'website_hr_recruitment',
        "stock"
        
    ],
    # 'base_setup', 'product', 'analytic', 'portal', 'digest'
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/pmr_itms_security.xml',
        'data/data.xml',
        'reports/print_out_qrcode_it/qr_code_it_report_lot_pc.xml',
        'reports/print_out_qrcode_it/qr_code_it_templates_lot_pc.xml',
        'reports/print_out_qrcode_printer/qr_code_it_report_printer.xml',
        'reports/print_out_qrcode_printer/qr_code_it_templates_printer.xml',
        'reports/print_out_qrcode_router/qr_code_it_report_router.xml',
        'reports/print_out_qrcode_router/qr_code_it_templates_router.xml',
        'reports/print_out_qrcode_switch/qr_code_it_report_switch.xml',
        'reports/print_out_qrcode_switch/qr_code_it_templates_switch.xml',
        'reports/print_out_qrcode_wifi/qr_code_it_report_wifi.xml',
        'reports/print_out_qrcode_wifi/qr_code_it_templates_wifi.xml',
        'views/pmr_itms_request_troubleshooting.xml',
        'views/pmr_itms_request_development.xml',
        'views/pmr_itms_completion_troubleshooting.xml',
        'views/pmr_itms_completion_development.xml',
        'views/pmr_itms_memo_pengajuan_pembelian_barang.xml',
        'views/pmr_itms_memo_pengajuan_permintaan_barang.xml',
        'views/pmr_itms_panitera_assets.xml',
        'views/pmr_itms_config.xml',
        'views/pmr_itms_hardware_software.xml',
        'views/pmr_itms_hardware_software.xml',
        'views/pmr_itms_maintenance.xml',
        'views/pmr_itms_user_access.xml',
        'views/pmr_itms_completion_user_access.xml',
        'views/pmr_itms_handover_it.xml',
        'wizard/handover_from_grn.xml'
     
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
    'license':'LGPL-3',
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
