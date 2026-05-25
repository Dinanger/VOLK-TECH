from odoo import models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            for line in order.order_line:
                if line.product_id.qty_available < line.product_uom_qty:
                    raise UserError(
                        f"No hay stock suficiente para el producto: {line.product_id.name}"
                    )
        return super().action_confirm()