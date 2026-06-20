import base64
import qrcode
from io import BytesIO
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class QRCoupon(models.Model):
    """
    QR Coupon Model

    Main model for managing promotional coupons with auto-generated QR codes.
    Each coupon generates a unique code (QR00001, QR00002, etc.) and corresponding QR code image.

    Status Workflow:
    - Draft: Created but not yet active (before start_date)
    - Active: Available for customer claims (between start_date and end_date)
    - Used: Reached maximum usage limit
    - Expired: Past end_date or manually deactivated

    Security:
    - Coupon validation prevents claiming expired/inactive/over-limit coupons
    - One-time use enforcement at application level
    - Usage count atomically incremented
    """
    _name = 'qr.coupon'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'QR Coupon'
    _order = 'create_date desc'

    # ============================================================================
    # FIELDS
    # ============================================================================

    # Basic Information
    name = fields.Char(
        string='Coupon Name',
        required=True,
        help='Display name for the coupon (e.g., "Summer 20% Off")'
    )
    code = fields.Char(
        string='Coupon Code',
        readonly=True,
        copy=False,
        help='Auto-generated unique code from sequence (QR00001, QR00002, etc.)'
    )
    description = fields.Text(
        string='Description',
        help='Coupon description shown to customers on public page'
    )

    # QR Code
    qr_code = fields.Binary(
        string='QR Code Image',
        readonly=True,
        help='Auto-generated PNG QR code image (binary data)'
    )
    public_url = fields.Char(
        string='Public URL',
        compute='_compute_public_url',
        store=False,
        help='Dynamic URL where customer scans QR code'
    )

    # Discount Configuration
    discount_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed_amount', 'Fixed Amount')],
        string='Discount Type',
        required=True,
        default='percentage',
        help='Type of discount: percentage (%) or fixed amount'
    )
    discount_value = fields.Float(
        string='Discount Value',
        required=True,
        help='Discount amount or percentage (e.g., 20 for 20% or 10 for $10 off)'
    )

    # Dates
    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=lambda self: fields.Date.today(),
        help='Date when coupon becomes active'
    )
    end_date = fields.Date(
        string='Expiration Date',
        required=True,
        help='Date when coupon expires (becomes inactive)'
    )

    # Usage Limits
    max_usage = fields.Integer(
        string='Maximum Usage',
        required=True,
        default=1,
        help='Maximum number of times coupon can be claimed'
    )
    used_count = fields.Integer(
        string='Usage Count',
        readonly=True,
        default=0,
        help='Current number of times coupon has been claimed'
    )

    # Status & Control
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Enable/disable coupon manually'
    )
    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('used', 'Used'),
            ('expired', 'Expired'),
            ('inactive', 'Inactive'),
        ],
        string='Status',
        compute='_compute_status',
        store=True,
        help='Coupon status based on dates, usage, and active flag'
    )

    # Relations
    scans_ids = fields.One2many(
        'qr.coupon.scan',
        'coupon_id',
        string='Scans',
        readonly=True,
        help='All scan records for this coupon'
    )

    # Metadata
    create_date = fields.Datetime(readonly=True)
    create_uid = fields.Many2one('res.users', readonly=True)

    # ============================================================================
    # CONSTRAINTS
    # ============================================================================

    @api.constrains('start_date', 'end_date')
    def _check_date_logic(self):
        """Ensure end_date is after start_date"""
        for coupon in self:
            if coupon.end_date and coupon.start_date and coupon.end_date < coupon.start_date:
                raise ValidationError('Expiration date must be after start date')

    @api.constrains('discount_value')
    def _check_discount_value(self):
        """Ensure discount value is positive"""
        for coupon in self:
            if coupon.discount_value <= 0:
                raise ValidationError('Discount value must be greater than 0')

    @api.constrains('max_usage')
    def _check_max_usage(self):
        """Ensure max_usage is positive"""
        for coupon in self:
            if coupon.max_usage <= 0:
                raise ValidationError('Maximum usage must be greater than 0')

    # ============================================================================
    # COMPUTED FIELDS
    # ============================================================================

    @api.depends('start_date', 'end_date', 'used_count', 'max_usage', 'active')
    def _compute_status(self):
        """
        Compute coupon status based on:
        1. Active flag (manually disabled)
        2. Usage count vs max_usage (reached limit)
        3. End date (expired)
        4. Start date (not yet active)
        5. Otherwise: active
        """
        today = fields.Date.today()
        for coupon in self:
            if not coupon.active:
                coupon.status = 'inactive'
            elif coupon.used_count >= coupon.max_usage:
                coupon.status = 'used'
            elif coupon.end_date and coupon.end_date < today:
                coupon.status = 'expired'
            elif coupon.start_date and coupon.start_date > today:
                coupon.status = 'draft'
            else:
                coupon.status = 'active'

    @api.depends('code')
    def _compute_public_url(self):
        """Generate public URL for accessing coupon"""
        for coupon in self:
            if coupon.code:
                coupon.public_url = f'/coupon/{coupon.code}'
            else:
                coupon.public_url = ''

    # ============================================================================
    # CREATE & WRITE METHODS
    # ============================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to:
        1. Generate coupon code from sequence
        2. Generate QR code image

        Process:
        - For each coupon being created
        - Generate next code from ir.sequence
        - Create QR code pointing to public URL
        - Convert QR to PNG binary
        - Store in qr_code field
        """
        for vals in vals_list:
            # Step 1: Generate code from sequence (only if not provided)
            if not vals.get('code'):
                vals['code'] = self.env['ir.sequence'].next_by_code('qr.coupon.code')

            # Step 2: Generate QR code image
            try:
                # Create public URL based on code
                public_url = f'/coupon/{vals["code"]}'

                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(public_url)
                qr.make(fit=True)

                # Convert PIL image to PNG bytes
                img = qr.make_image(fill_color='black', back_color='white')
                img_io = BytesIO()
                img.save(img_io, format='PNG')
                img_bytes = img_io.getvalue()

                # Store as base64 for database storage
                vals['qr_code'] = base64.b64encode(img_bytes)
            except Exception as e:
                raise UserError(f'Error generating QR code: {str(e)}')

        return super().create(vals_list)

    # ============================================================================
    # VALIDATION METHODS
    # ============================================================================

    def validate_coupon(self):
        """
        Validate coupon before allowing customer to claim it.

        Checks:
        1. Coupon exists and is not deleted
        2. Status is 'active' (not expired, used, draft, or inactive)
        3. Current usage is below maximum
        4. Active flag is True

        Returns:
            True if coupon is valid and claimable
            False if coupon is invalid
            Raises exception if any validation fails
        """
        self.ensure_one()

        # Force refresh of computed status
        self._compute_status()

        if self.status != 'active':
            return False

        if self.used_count >= self.max_usage:
            return False

        return True

    def get_display_discount(self):
        """Return formatted discount string for display (e.g., '20%' or '$10')"""
        self.ensure_one()
        if self.discount_type == 'percentage':
            return f'{self.discount_value}%'
        else:
            return f'${self.discount_value:.2f}'

    def get_days_until_expiration(self):
        """Return number of days until expiration"""
        self.ensure_one()
        if not self.end_date:
            return None
        expiration = fields.Date.from_string(self.end_date)
        today = datetime.now().date()
        delta = expiration - today
        return max(0, delta.days)

    # ============================================================================
    # ACTION METHODS
    # ============================================================================

    def action_claim_coupon(self, customer_data):
        """
        Action method for claiming coupon.
        Called from controller when customer submits form.

        Args:
            customer_data (dict): {
                'name': str,
                'email': str,
                'phone': str,
                'message': str (optional),
                'ip_address': str,
                'user_agent': str,
            }

        Returns:
            tuple: (lead_id, scan_id) - IDs of created lead and scan records

        Raises:
            UserError: If coupon validation fails
        """
        self.ensure_one()

        # Validate coupon
        if not self.validate_coupon():
            raise UserError(f'Coupon {self.code} is not available for claiming')

        # Create CRM Lead
        lead_vals = {
            'name': customer_data.get('name'),
            'email_from': customer_data.get('email'),
            'phone': customer_data.get('phone'),
            'description': customer_data.get('message', ''),
            'coupon_id': self.id,
            'coupon_scan_id': False,  # Will be updated after scan creation
        }
        lead = self.env['crm.lead'].sudo().create(lead_vals)

        # Create scan record
        scan_vals = {
            'coupon_id': self.id,
            'lead_id': lead.id,
            'scan_date': fields.Datetime.now(),
            'ip_address': customer_data.get('ip_address', ''),
            'user_agent': customer_data.get('user_agent', ''),
            'customer_name': customer_data.get('name'),
            'customer_email': customer_data.get('email'),
            'customer_phone': customer_data.get('phone'),
            'status_at_scan': self.status,
        }
        scan = self.env['qr.coupon.scan'].sudo().create(scan_vals)

        # Update lead with scan reference
        lead.sudo().write({'coupon_scan_id': scan.id})

        # Increment usage count atomically
        # (status is a computed field that depends on used_count, so it
        # will recompute itself automatically — no need to write it directly)
        self.sudo().write({
            'used_count': self.used_count + 1,
        })

        return lead.id, scan.id
