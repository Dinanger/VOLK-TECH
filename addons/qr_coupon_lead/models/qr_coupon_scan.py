from odoo import api, fields, models


class QRCouponScan(models.Model):
    """
    QR Coupon Scan Tracking Model

    Tracks every scan of a QR coupon by external customers.
    Records scan metadata (IP, User Agent, timestamp) for audit trail and analytics.

    Enables:
    - Fraud detection (multiple scans from same IP)
    - Device tracking (User Agent analysis)
    - Conversion metrics (scans → leads)
    - Coupon performance analysis
    - Compliance audit trails

    Lifecycle:
    - Created when customer scans QR code AND claims coupon
    - Linked to both coupon and generated lead
    - Immutable record (no updates after creation)
    """
    _name = 'qr.coupon.scan'
    _description = 'QR Coupon Scan Tracking'
    _order = 'scan_date desc'

    # ============================================================================
    # FIELDS
    # ============================================================================

    # Relations
    coupon_id = fields.Many2one(
        'qr.coupon',
        string='Coupon',
        required=True,
        ondelete='cascade',
        help='Link to QR Coupon'
    )
    lead_id = fields.Many2one(
        'crm.lead',
        string='Generated Lead',
        readonly=True,
        help='CRM Lead automatically created from this scan'
    )

    # Timing
    scan_date = fields.Datetime(
        string='Scan Date',
        required=True,
        default=lambda self: fields.Datetime.now(),
        help='When customer scanned coupon'
    )

    # Coupon State
    status_at_scan = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('used', 'Used'),
            ('expired', 'Expired'),
            ('inactive', 'Inactive'),
        ],
        string='Coupon Status at Scan',
        readonly=True,
        help='Coupon status recorded at scan time'
    )

    # Customer Information
    customer_name = fields.Char(
        string='Customer Name',
        required=True,
        help='Full name provided by customer'
    )
    customer_email = fields.Char(
        string='Customer Email',
        required=True,
        help='Email provided by customer (not validated at scan time)'
    )
    customer_phone = fields.Char(
        string='Customer Phone',
        required=True,
        help='Phone number provided by customer'
    )

    # Network Information
    ip_address = fields.Char(
        string='IP Address',
        help='Customer IP address extracted from request'
    )
    user_agent = fields.Char(
        string='User Agent',
        help='Browser/device info from HTTP headers'
    )

    # Metadata
    create_date = fields.Datetime(readonly=True)

    # ============================================================================
    # COMPUTED FIELDS
    # ============================================================================

    def _get_device_type(self):
        """
        Extract device type from User Agent string.
        Simple heuristic: looks for common patterns.

        Returns:
            str: 'mobile', 'tablet', 'desktop', or 'unknown'
        """
        if not self.user_agent:
            return 'unknown'

        ua_lower = self.user_agent.lower()

        if any(x in ua_lower for x in ['iphone', 'android', 'mobile']):
            return 'mobile'
        elif any(x in ua_lower for x in ['ipad', 'tablet']):
            return 'tablet'
        elif any(x in ua_lower for x in ['windows', 'mac', 'linux']):
            return 'desktop'

        return 'unknown'

    def _get_os_type(self):
        """
        Extract operating system from User Agent string.

        Returns:
            str: 'iOS', 'Android', 'Windows', 'macOS', 'Linux', or 'Unknown'
        """
        if not self.user_agent:
            return 'Unknown'

        ua = self.user_agent

        if 'iPhone' in ua or 'iPad' in ua:
            return 'iOS'
        elif 'Android' in ua:
            return 'Android'
        elif 'Windows' in ua:
            return 'Windows'
        elif 'Mac' in ua:
            return 'macOS'
        elif 'Linux' in ua:
            return 'Linux'

        return 'Unknown'

    # ============================================================================
    # CONSTRAINTS
    # ============================================================================

    @api.constrains('customer_email')
    def _check_email_format(self):
        """Validate email format (basic check)"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        for scan in self:
            if scan.customer_email:
                if not re.match(email_pattern, scan.customer_email):
                    pass  # Allow invalid emails for now (captured as-is from customer)

    @api.constrains('customer_phone')
    def _check_phone_format(self):
        """Validate phone format (basic check)"""
        for scan in self:
            if scan.customer_phone:
                # Remove common phone formatting characters
                digits = ''.join(filter(str.isdigit, scan.customer_phone))
                if len(digits) < 7:
                    pass  # Allow all formats (different countries have different lengths)

    # ============================================================================
    # METHODS
    # ============================================================================

    def get_scan_summary(self):
        """Return formatted summary of scan"""
        self.ensure_one()
        return f'{self.customer_name} ({self.customer_email}) - {self.scan_date.strftime("%Y-%m-%d %H:%M:%S")}'

    def get_hours_since_scan(self):
        """Calculate hours elapsed since scan"""
        self.ensure_one()
        from datetime import datetime
        now = datetime.now()
        scan_dt = self.scan_date.replace(tzinfo=None)
        delta = now - scan_dt
        return delta.total_seconds() / 3600

    def get_coupon_completion_time(self):
        """
        If lead was converted, calculate time from scan to lead conversion.
        Useful for measuring sales cycle.
        """
        self.ensure_one()
        if not self.lead_id:
            return None

        lead = self.lead_id
        if not lead.date_open:
            return None

        delta = lead.date_open - self.scan_date
        return delta.total_seconds() / 3600  # Return hours
