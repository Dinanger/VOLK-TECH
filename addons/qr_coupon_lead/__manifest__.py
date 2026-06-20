{
    'name': 'QR Coupon Lead Generator',
    'version': '18.0.1.0.0',
    'category': 'Sales/CRM',
    'author': 'Volk Tech',
    'summary': 'Automated QR Coupon system generating CRM Leads when customers scan QR codes',
    'description': '''
    Smart QR Coupon System for Odoo 18 Community

    Features:
    - Create and manage promotional coupons with unique QR codes
    - Auto-generate sequential coupon codes (QR00001, QR00002, etc.)
    - Public website interface for coupon claim without authentication
    - Automatic CRM Lead creation on coupon claim
    - Comprehensive scan tracking (IP, User Agent, timestamps)
    - KPI Dashboard with conversion metrics
    - Coupon status management (Draft, Active, Used, Expired)
    - One-time usage validation per coupon
    - Discount management (Percentage or Fixed Amount)
    - Production-ready security implementation

    Technical Stack:
    - Odoo 18 Community (no Enterprise features)
    - Python-QRCode for QR generation
    - PostgreSQL for scan tracking
    - QWeb templates for public interface
    ''',
    'depends': [
        'base',
        'mail',
        'sale_management',
        'crm',
        'website',
    ],
    'external_dependencies': {
        'python': ['qrcode', 'Pillow'],
    },
    'data': [
        # Security
        'security/security_groups.xml',
        'security/ir.model.access.csv',

        # Data (Sequences)
        'data/sequence_data.xml',

      'views/qr_coupon_views.xml',
      'views/qr_coupon_scan_views.xml',
      'views/dashboard_views.xml',
      'views/menus.xml',

        # Website
        'website/templates/coupon_page.xml',
        'website/templates/coupon_form.xml',
        'website/templates/success_page.xml',
        'website/templates/error_pages.xml',

        # Reports
        'reports/coupon_report.xml',
        'reports/lead_report.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'qr_coupon_lead/website/static/css/coupon_style.css',
            'qr_coupon_lead/website/static/js/coupon_form.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
