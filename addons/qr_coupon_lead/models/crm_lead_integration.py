from odoo import api, fields, models


class CRMLead(models.Model):
    """
    CRM Lead Model Extension

    Extends the standard crm.lead model to add coupon-specific fields.
    Links leads back to their source coupon and scan tracking record.

    This allows:
    - Attribution tracking (lead source = QR Coupon)
    - Coupon performance analysis (which coupons convert best)
    - Lead lifecycle analysis (time from scan to conversion)
    - Marketing ROI calculation
    """
    _inherit = 'crm.lead'

    # ============================================================================
    # NEW FIELDS FOR COUPON INTEGRATION
    # ============================================================================

    coupon_id = fields.Many2one(
        'qr.coupon',
        string='Related Coupon',
        readonly=True,
        help='QR Coupon that generated this lead'
    )
    coupon_scan_id = fields.Many2one(
        'qr.coupon.scan',
        string='Coupon Scan Record',
        readonly=True,
        help='Scan tracking record for audit trail'
    )

    # ============================================================================
    # DEFAULTS FOR COUPON-GENERATED LEADS
    # ============================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to set source='QR Coupon' for leads created from coupons.

        If coupon_id is present in creation values, automatically:
        - Set source_id to find/create 'QR Coupon' UTM source
        - Add label for tracking
        """
        source = None
        for vals in vals_list:
            if vals.get('coupon_id'):
                if source is None:
                    source = self.env['utm.source'].sudo().search([
                        ('name', '=', 'QR Coupon')
                    ], limit=1)

                    if not source:
                        source = self.env['utm.source'].sudo().create({
                            'name': 'QR Coupon',
                        })

                vals['source_id'] = source.id

        return super().create(vals_list)

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def get_coupon_discount_display(self):
        """Get formatted discount from related coupon"""
        self.ensure_one()
        if self.coupon_id:
            return self.coupon_id.get_display_discount()
        return ''

    def get_scan_to_lead_time_hours(self):
        """Calculate hours from coupon scan to lead creation"""
        self.ensure_one()
        if not self.coupon_scan_id:
            return None

        time_diff = self.create_date - self.coupon_scan_id.scan_date
        return time_diff.total_seconds() / 3600

    def action_view_coupon(self):
        """Action to jump to related coupon"""
        self.ensure_one()
        if not self.coupon_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'qr.coupon',
            'res_id': self.coupon_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_scan(self):
        """Action to jump to scan record"""
        self.ensure_one()
        if not self.coupon_scan_id:
            return

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'qr.coupon.scan',
            'res_id': self.coupon_scan_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
