import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CRMLead(models.Model):
    """
    CRM Lead Model Extension
    """
    _inherit = 'crm.lead'

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

    @api.model_create_multi
    def create(self, vals_list):
        source = None
        for vals in vals_list:
            if vals.get('coupon_id'):
                if source is None:
                    source = self.env['utm.source'].sudo().search(
                        [('name', '=', 'QR Coupon')], limit=1
                    )
                    if not source:
                        source = self.env['utm.source'].sudo().create(
                            {'name': 'QR Coupon'}
                        )
                vals['source_id'] = source.id
        return super().create(vals_list)

    @staticmethod
    def _apply_discount_to_lines(lines, coupon):
        """Apply coupon discount to a recordset of sale.order.line."""
        if coupon.discount_type == 'percentage':
            for line in lines:
                line.discount = coupon.discount_value
        elif coupon.discount_type == 'fixed_amount':
            total = sum(
                line.price_unit * line.product_uom_qty for line in lines
            )
            if total > 0:
                for line in lines:
                    line_total = line.price_unit * line.product_uom_qty
                    if line_total > 0:
                        pct = round(
                            coupon.discount_value / total * 100, 2
                        )
                        line.discount = pct

    def get_coupon_discount_display(self):
        self.ensure_one()
        return self.coupon_id.get_display_discount() if self.coupon_id else ''

    def get_scan_to_lead_time_hours(self):
        self.ensure_one()
        if not self.coupon_scan_id:
            return None
        return (
            self.create_date - self.coupon_scan_id.scan_date
        ).total_seconds() / 3600

    def action_view_coupon(self):
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


class SaleOrder(models.Model):
    """
    Sale Order Extension

    FIX DEFINITIVO para Odoo 18:

    En Odoo 18 el botón "Nueva Cotización" del CRM es un type="action"
    que apunta a sale_action_quotations_new — una window action XML pura.
    NUNCA pasa por ningún método Python de crm.lead. Por eso los overrides
    de _action_new_quotation / action_new_quotation no sirven.

    La estrategia correcta es interceptar SaleOrder.create():
    cuando se crea una cotización vinculada a un opportunity (via
    opportunity_id, que Odoo 18 setea automáticamente), leemos el cupón
    del lead y lo escribimos en qr_coupon_id para que persista.
    """
    _inherit = 'sale.order'

    qr_coupon_id = fields.Many2one(
        'qr.coupon',
        string='QR Coupon',
        readonly=True,
        help='Cupón QR vinculado desde el lead de origen',
    )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)

        for order in orders:
            # opportunity_id lo pone Odoo 18 automáticamente cuando
            # el vendedor presiona "Nueva Cotización" desde el CRM lead
            if not order.opportunity_id:
                continue

            lead = order.opportunity_id
            coupon = lead.coupon_id
            if not coupon:
                continue

            try:
                discount_label = coupon.get_display_discount()
                note = (
                    f'[QR Coupon {coupon.code}] '
                    f'Descuento aplicado: {discount_label}'
                )
                existing_note = order.note or ''
                order.sudo().write({
                    'note': (existing_note + '\n' + note).strip(),
                    'qr_coupon_id': coupon.id,
                })
                _logger.info(
                    'Cupón %s vinculado a cotización %s (lead %s)',
                    coupon.code, order.name, lead.id
                )
            except Exception:
                _logger.exception(
                    'Error vinculando cupón al crear cotización %s', order.id
                )

        return orders


class SaleOrderLine(models.Model):
    """
    Auto-apply coupon discount when a line is added to a quotation
    that has a linked QR coupon.

    Lee qr_coupon_id desde sale.order (campo persistente en BD).
    Funciona tanto en la creación inicial como cuando el vendedor
    agrega productos manualmente desde la pantalla de la cotización.
    """
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)

        for line in lines:
            if line.display_type:
                continue

            coupon = line.order_id.qr_coupon_id
            if not coupon:
                continue

            try:
                if coupon.discount_type == 'percentage':
                    line.discount = coupon.discount_value

                elif coupon.discount_type == 'fixed_amount':
                    line_total = line.price_unit * line.product_uom_qty
                    if line_total > 0:
                        line.discount = round(
                            coupon.discount_value / line_total * 100, 2
                        )
                _logger.info(
                    'Descuento cupón %s aplicado a línea %s (orden %s)',
                    coupon.code, line.id, line.order_id.name
                )
            except Exception:
                _logger.exception(
                    'Error aplicando descuento cupón %s a línea %s',
                    coupon.code, line.id
                )

        return lines
