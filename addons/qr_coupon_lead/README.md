# QR Coupon Lead Generator - Odoo 18 Community Module

A professional, production-ready Odoo 18 Community module that implements an automated QR Coupon system. Customers scan QR codes to access promotional coupons, and the system automatically generates CRM Leads with comprehensive tracking capabilities.

## 🎯 Key Features

### Coupon Management
- **Auto-generated unique codes**: Sequential format (QR00001, QR00002, etc.)
- **QR code generation**: Automatic PNG QR codes pointing to public URLs
- **Flexible discounts**: Support for both percentage and fixed-amount discounts
- **Usage tracking**: Per-coupon usage limits with real-time counting
- **Status management**: Draft, Active, Used, Expired states
- **Date-based validity**: Start and end dates for time-limited promotions

### Public Interface
- **Unauthenticated access**: Customers don't need Odoo accounts
- **Clean form interface**: Name, email, phone fields
- **Real-time validation**: Client-side + server-side validation
- **Responsive design**: Mobile-friendly interface
- **Professional UX**: Bootstrap 5 styling with custom CSS

### Lead Generation
- **Automatic creation**: CRM Leads automatically created on coupon claim
- **Contact tracking**: Name, email, phone captured
- **Coupon attribution**: Links leads back to source coupon
- **Scan audit trail**: IP address and device info recorded
- **Source tracking**: All leads marked as "QR Coupon" source

### Analytics & Reporting
- **Dashboard**: KPI metrics (total coupons, scans, leads, conversion rate)
- **Graph views**: Visual analysis by status, discount type
- **Scan tracking**: Detailed audit trail with timestamps and device info
- **Performance reports**: PDF reports for coupon performance
- **Conversion metrics**: Track scan-to-lead conversion rates

### Security
- **Public authentication**: `auth='public'` for open access
- **Input validation**: Email, phone, name format checking
- **XSS protection**: Auto-escaping in QWeb templates
- **SQL injection prevention**: ORM-based queries only
- **CSRF protection**: Automatic token validation
- **Access control**: Role-based permissions (Manager, Viewer, Creator)

---

## 📦 Installation

### Prerequisites
- Odoo 18 Community Edition
- Python 3.11+
- PostgreSQL 12+
- Docker (optional, for containerized deployment)

### Required Python Dependencies
```bash
pip install qrcode[pil]
pip install Pillow
```

### Installation Steps

1. **Clone/Download the module** into your Odoo addons directory:
```bash
cd /path/to/odoo/addons
git clone <repo-url> qr_coupon_lead
# or
cp -r qr_coupon_lead /path/to/odoo/addons/
```

2. **Update Odoo Apps List**:
   - Go to Apps → Update Apps List (or run `odoo-bin -d <database> -c <config> --update-module-list`)

3. **Install the module**:
   - Search for "QR Coupon" in Apps
   - Click Install

4. **Configure initial data** (optional):
   - Create your first coupon in Sales → QR Coupons → Coupons
   - Test the public URL

### Docker Deployment

If using Docker Compose:

```yaml
# In your docker-compose.yml, ensure addons_path includes this module
services:
  odoo:
    volumes:
      - ./addons:/mnt/extra-addons
    environment:
      - ADDONS_PATH=/mnt/extra-addons
```

Then restart Odoo:
```bash
docker-compose restart
```

---

## 🚀 Quick Start Guide

### 1. Create a Coupon

1. Navigate to **Sales → QR Coupons → Coupons**
2. Click **Create**
3. Fill in the form:
   - **Name**: "Summer 20% Off"
   - **Discount Type**: Percentage
   - **Discount Value**: 20
   - **Start Date**: Today
   - **End Date**: 30 days from today
   - **Maximum Usage**: 100
4. Click **Save**

The system will automatically:
- Generate unique code (QR00001, QR00002, etc.)
- Create QR code image
- Set status to Active (if dates are valid)

### 2. Scan QR Code

Public URL format: `http://your-domain:8069/coupon/QR00001`

Share this URL via:
- Email campaigns
- Social media
- Printed materials (with actual QR code)
- Website banners

### 3. Customer Flow

When customer scans QR code:

1. **Coupon Page Displayed**
   - Shows coupon name and discount
   - Displays QR code image
   - Shows expiration date and usage limits

2. **Customer Fills Form**
   - Full Name (required)
   - Email (required)
   - Phone (required)
   - Optional message

3. **Form Submission**
   - Server validates all inputs
   - Creates CRM Lead automatically
   - Creates scan tracking record
   - Increments coupon usage counter

4. **Success Page**
   - Confirms coupon claim
   - Shows coupon code for reference
   - Displays discount details
   - Thanks customer

### 4. View Results

#### Coupon Management
- **Sales → QR Coupons → Coupons**: View all coupons with status indicators
- **Status colors**: Draft (gray), Active (blue), Used (red), Expired (muted)
- **Tree view**: Sort by code, name, discount, status, usage count
- **Kanban view**: Group coupons by status for visual workflow

#### Lead Tracking
- **Sales → CRM → Leads**: Search for leads with source = "QR Coupon"
- **Lead details**: View related coupon and scan information
- **Conversion tracking**: Monitor which coupons generate most leads

#### Scan Analytics
- **Sales → QR Coupons → Scan Tracking**: View all coupon scans
- **Customer info**: Name, email, phone, IP address
- **Scan details**: Timestamp, coupon status at scan time
- **Device tracking**: User Agent for device/OS detection

#### Dashboard
- **Sales → QR Coupons → Dashboard**: View KPI metrics
- **Pie chart**: Coupon status distribution
- **Line chart**: Scans over time
- **Pivot analysis**: Custom report building

---

## 🏗️ Architecture

### Module Structure
```
qr_coupon_lead/
├── models/
│   ├── qr_coupon.py              # Main coupon model (350+ lines)
│   ├── qr_coupon_scan.py          # Scan tracking model (150+ lines)
│   └── crm_lead_integration.py   # CRM Lead extension (50+ lines)
├── controllers/
│   └── coupon_controller.py       # Public routes & form handling (400+ lines)
├── views/
│   ├── qr_coupon_views.xml       # Coupon form/tree/kanban/search
│   ├── qr_coupon_scan_views.xml  # Scan form/tree/search
│   ├── dashboard_views.xml       # KPI graphs and pivot
│   └── menus.xml                 # Navigation menus
├── website/
│   ├── templates/
│   │   ├── assets.xml            # CSS/JS asset registration
│   │   ├── coupon_page.xml       # Main coupon display
│   │   ├── coupon_form.xml       # Claim form component
│   │   ├── success_page.xml      # Success message
│   │   └── error_pages.xml       # Error messages
│   └── static/
│       ├── css/
│       │   └── coupon_style.css  # Professional styling (450+ lines)
│       └── js/
│           └── coupon_form.js    # Client-side validation (350+ lines)
├── security/
│   ├── security_groups.xml       # Role-based access
│   └── ir.model.access.csv       # Model-level permissions
├── data/
│   ├── sequence_data.xml         # Coupon code sequence
│   └── initial_data.xml          # Default setup data
├── reports/
│   ├── coupon_report.xml         # Coupon performance PDF
│   └── lead_report.xml           # Lead generation PDF
├── __manifest__.py               # Module metadata
├── __init__.py                   # Module initialization
└── README.md                     # This file
```

### Data Models

#### `qr.coupon` (Main Coupon Model)
**Purpose**: Central model managing all coupon data and business logic

**Key Fields**:
- `code` (Char): Auto-generated unique code (QR00001, etc.)
- `qr_code` (Binary): PNG image of QR code
- `status` (Selection): Computed field (Draft, Active, Used, Expired)
- `discount_type` (Selection): Percentage or Fixed Amount
- `discount_value` (Float): Discount amount/percentage
- `start_date` (Date): When coupon becomes active
- `end_date` (Date): When coupon expires
- `max_usage` (Integer): Maximum claim limit
- `used_count` (Integer): Current usage count
- `active` (Boolean): Manual enable/disable

**Key Methods**:
- `create()`: Generate code and QR code automatically
- `_compute_status()`: Determine status based on dates/usage/active flag
- `validate_coupon()`: Check if coupon is claimable
- `action_claim_coupon()`: Process claim, create lead and scan

**Security**: Only managers can create/edit coupons

#### `qr.coupon.scan` (Scan Tracking Model)
**Purpose**: Audit trail and analytics for coupon scans

**Key Fields**:
- `coupon_id` (Many2one): Link to coupon
- `lead_id` (Many2one): Generated CRM lead
- `scan_date` (Datetime): When scanned
- `customer_name` (Char): Customer name from form
- `customer_email` (Char): Customer email from form
- `customer_phone` (Char): Customer phone from form
- `ip_address` (Char): Customer IP address
- `user_agent` (Char): Browser/device info
- `status_at_scan` (Selection): Coupon status when scanned

**Key Methods**:
- `_get_device_type()`: Extract device type from User Agent
- `_get_os_type()`: Extract operating system
- `get_scan_summary()`: Formatted scan details
- `get_coupon_completion_time()`: Time from scan to lead conversion

**Security**: Read-only, created automatically by controller

#### `crm.lead` (Extended Model)
**Purpose**: Link CRM leads back to source coupons

**Additional Fields**:
- `coupon_id` (Many2one): Source coupon
- `coupon_scan_id` (Many2one): Scan record for audit trail

**Automatic Setup**:
- `source_id`: Set to 'QR Coupon' automatically
- `partner_name`: Pre-populated from form

---

## 🔒 Security Model

### Authentication & Authorization

**Public Routes** (No Login Required):
- `/coupon/<code>` - View coupon and form
- `/coupon/<code>/claim` - Submit form
- `/coupon/success/<code>` - Show success message
- `/coupon/error/<type>` - Show error message

**Access Control**:
- **QR Coupon Manager**: Full CRUD on coupons, view all analytics
- **QR Coupon Viewer**: Read-only access to coupons and scans
- **QR Coupon Lead Creator**: View leads created from coupons (includes CRM user group)

### Input Validation

**Name Field**:
- Regex: `^[a-zA-Z\s\-']+$` (letters, spaces, hyphens, apostrophes only)
- Length: 2-100 characters
- Server-side validation (prevents code injection)

**Email Field**:
- Regex: `^[^\s@]+@[^\s@]+\.[^\s@]+$` (basic email format)
- Server-side validation (prevents XSS)

**Phone Field**:
- Minimum 7 digits extracted from input
- Accepts various formats: (555) 123-4567, 555-123-4567, 5551234567, etc.
- Server-side validation

**Message Field** (Optional):
- Maximum 500 characters
- Trimmed before storage
- Escaped in display (XSS prevention)

### Threat Mitigation

| Threat | Mitigation |
|--------|-----------|
| SQL Injection | ORM-based queries only, no raw SQL |
| XSS (Cross-Site Scripting) | QWeb auto-escaping, no JavaScript injection |
| CSRF (Cross-Site Request Forgery) | Automatic CSRF token validation via Odoo framework |
| Brute Force | Rate limiting recommended at nginx level |
| Data Exposure | `sudo()` used only for public lead/scan creation |
| Double Claiming | Application-level enforcement + UI validation |
| Coupon Reuse | Status validation prevents claiming used/expired coupons |

### Best Practices Implemented

✅ **Least Privilege**: `auth='public'` only for necessary routes
✅ **Input Validation**: Server-side validation of all form data
✅ **Output Encoding**: QWeb templates auto-escape content
✅ **Secure Defaults**: Coupons inactive by default, set dates for auto-activation
✅ **Audit Trail**: All scans logged with IP, User Agent, timestamp
✅ **Error Handling**: Graceful error messages without exposing internals
✅ **HTTPS Ready**: Full support for HTTPS in production

---

## 📊 Reporting & Analytics

### Built-in Views

**Coupon Management**:
- **Tree View**: List all coupons with status indicators, sortable by any column
- **Kanban View**: Grouped by status for visual workflow (Draft → Active → Used)
- **Form View**: Full coupon details with QR code display
- **Search View**: Filter by status, discount type, active state

**Scan Tracking**:
- **Tree View**: All scans with customer info, timestamps, IP addresses
- **Form View**: Detailed scan information with device detection
- **Search/Filter**: By coupon, status, date range, has-lead/no-lead

**Dashboard**:
- **Pie Chart**: Coupon distribution by status
- **Line Chart**: Scans over time (trends)
- **Pivot View**: Custom analysis (rows/columns/values)

### Key Metrics

```
Total Coupons         = COUNT(qr.coupon)
Active Coupons        = COUNT(qr.coupon WHERE status='active')
Total Scans           = COUNT(qr.coupon.scan)
Total Leads Generated = COUNT(crm.lead WHERE source='QR Coupon')
Conversion Rate       = (Total Leads / Total Scans) × 100
Usage Rate            = (SUM(used_count) / SUM(max_usage)) × 100
```

### PDF Reports

**Coupon Performance Report**:
- Coupon details (name, code, discount, dates)
- Usage statistics (claims, maximum, remaining)
- Complete scan audit trail

**Lead Generation Report**:
- All leads from coupon claims
- Customer contact information
- Lead status and stage
- Coupon attribution

---

## 🚀 Production Deployment

### Pre-Deployment Checklist

- [ ] Install in staging environment first
- [ ] Create test coupons and verify QR code generation
- [ ] Test public URL from mobile device
- [ ] Verify form validation (valid and invalid inputs)
- [ ] Check CRM lead creation and scan tracking
- [ ] Review access control settings for your organization
- [ ] Configure HTTPS and domain name
- [ ] Set up email notifications for new leads
- [ ] Test backup and restore procedures

### Docker Deployment

```bash
# Build the container
docker-compose build

# Start the services
docker-compose up -d

# Update module list
docker-compose exec odoo odoo-bin -d postgres --update-module-list

# Install the module
docker-compose exec odoo odoo-bin -d postgres -i qr_coupon_lead

# Restart Odoo
docker-compose restart odoo
```

### Environment Configuration

Update your `.env` and `odoo.conf`:

```ini
# odoo.conf
[options]
addons_path = /mnt/extra-addons
db_host = postgres.db
db_port = 5432
db_user = odoo
db_password = PASSWORD
http_port = 8069
proxy_mode = True
workers = 4
max_cron_threads = 1
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560
```

### Performance Optimization

**Database Indexes** (automatically created):
```sql
-- Auto-created by Odoo ORM
CREATE INDEX idx_qr_coupon_code ON qr_coupon(code);
CREATE INDEX idx_qr_coupon_status ON qr_coupon(status);
CREATE INDEX idx_qr_coupon_scan_coupon_id ON qr_coupon_scan(coupon_id);
CREATE INDEX idx_qr_coupon_scan_scan_date ON qr_coupon_scan(scan_date);
```

**Caching Recommendations**:
- Browser cache: QR code images (immutable resource)
- Server cache: Coupon status (5-minute TTL)
- CDN: Static assets (CSS, JavaScript, QR codes)

**Scaling Considerations**:
- Scan tracking can grow large; archive old records periodically
- Consider async processing for high-volume scan scenarios
- Implement rate limiting at nginx level (anti-spam)
- Use connection pooling for database

---

## 🔧 Configuration & Customization

### Customize Coupon Code Format

Edit `data/sequence_data.xml`:

```xml
<record id="seq_qr_coupon_code" model="ir.sequence">
    <field name="prefix">PROMO</field>       <!-- Change prefix -->
    <field name="padding">6</field>         <!-- Change zero-padding -->
    <field name="number_next">1000</field>  <!-- Start from different number -->
</record>
```

Result: PROMO001000, PROMO001001, etc.

### Customize Email Notifications

Create new module inheriting `qr_coupon_lead` to add email templates:

```python
from odoo import models

class QRCoupon(models.Model):
    _inherit = 'qr.coupon'

    def action_claim_coupon(self, customer_data):
        lead_id, scan_id = super().action_claim_coupon(customer_data)
        
        # Send email notification
        self.env['mail.template'].browse([
            self.env.ref('qr_coupon_lead.email_coupon_claimed').id
        ]).send_mail(self.id)
        
        return lead_id, scan_id
```

### Customize Website Templates

Inherit QWeb templates in a child module:

```xml
<template id="custom_coupon_page" inherit_id="qr_coupon_lead.coupon_page">
    <xpath expr="//div[@class='card-header']" position="replace">
        <!-- Your custom header -->
    </xpath>
</template>
```

### Add Custom Fields

Extend models in your custom module:

```python
from odoo import api, fields, models

class QRCoupon(models.Model):
    _inherit = 'qr.coupon'

    # Add custom field
    category = fields.Selection([
        ('summer', 'Summer Sale'),
        ('winter', 'Winter Sale'),
        ('clearance', 'Clearance'),
    ], string='Campaign Category')

    partner_id = fields.Many2one('res.partner', string='Partner')
```

---

## 📚 API Reference

### Coupon Model Methods

```python
# Validate if coupon is claimable
coupon = env['qr.coupon'].search([('code', '=', 'QR00001')])
if coupon.validate_coupon():
    # Coupon is active and available
    pass

# Get formatted discount
discount_str = coupon.get_display_discount()  # Returns "20%" or "$10.00"

# Get days until expiration
days = coupon.get_days_until_expiration()  # Returns number of days

# Claim coupon (create lead and scan)
lead_id, scan_id = coupon.action_claim_coupon({
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '(555) 123-4567',
    'message': 'Optional message',
    'ip_address': '192.168.1.100',
    'user_agent': 'Mozilla/5.0...',
})
```

### Controller Methods

```python
# From coupon_controller.py
controller = env['ir.http'].routing_map()

# Public routes (no login required)
GET  /coupon/<code>              # View coupon
POST /coupon/<code>/claim        # Submit form
GET  /coupon/success/<code>      # Show success
GET  /coupon/error/<error_type>  # Show error
```

### CRM Lead Fields

```python
# All coupon-generated leads have these fields set:
lead.coupon_id           # Link to source coupon
lead.coupon_scan_id      # Link to scan record
lead.source_id.name      # "QR Coupon"
lead.email_from          # From form
lead.phone               # From form
lead.partner_name        # Customer name from form
```

---

## 🐛 Troubleshooting

### Common Issues

**QR Code Not Generating**

```python
# Check if qrcode library is installed
python -c "import qrcode; print(qrcode.__version__)"

# If missing, install:
pip install qrcode[pil]
pip install Pillow
```

**Public URL Not Working**

```
# Check if route is registered
odoo-bin --scan-addons /path/to/addons

# Check website module is installed
# Go to Apps, search for "Website", ensure installed
```

**Lead Not Created**

```python
# Check if CRM module is installed
# Check if 'QR Coupon' source exists in CRM
env['crm.lead.source'].search([('name', '=', 'QR Coupon')])

# Check error logs
journalctl -u odoo --follow
```

**Form Validation Errors**

```javascript
// Check browser console for JavaScript errors
console.log('Coupon Form Debug:', window.CouponForm);

// Test validation functions
window.CouponForm.validateEmail('test@example.com');
window.CouponForm.validatePhone('5551234567');
```

### Debug Mode

Enable Odoo debug mode:

```python
# In odoo.conf
[options]
debug = True
log_level = debug

# Or via environment
export ODOO_LOG_LEVEL=debug
```

Then check logs:
```bash
tail -f /var/log/odoo/odoo.log
```

---

## 📞 Support & Contributing

### Issues & Bugs

Report issues with:
1. **Odoo Version**: `18.0`
2. **Python Version**: Output of `python --version`
3. **Error Log**: Full stack trace from logs
4. **Steps to Reproduce**: Exact steps that trigger the issue

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add my feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit pull request

### Enhancement Requests

- Additional coupon validation rules
- Multi-language support for form
- Advanced analytics (ML-based insights)
- Integration with email marketing platforms
- SMS notifications for coupon claims

---

## 📄 License

This module is licensed under the LGPL-3 License. See LICENSE file for details.

---

## 🎓 Additional Resources

- **Odoo Documentation**: https://www.odoo.com/documentation/18.0/
- **Odoo Development Guide**: https://www.odoo.com/documentation/18.0/developer.html
- **QRCode Library**: https://github.com/lincolnloop/python-qrcode
- **Bootstrap 5**: https://getbootstrap.com/docs/5.0/

---

**Module Version**: 18.0.1.0.0  
**Last Updated**: 2026-06-18  
**Author**: Volk Tech  
**License**: LGPL-3
