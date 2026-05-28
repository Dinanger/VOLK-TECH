from odoo import models, fields, api, exceptions
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # =====================================================
    # FIELDS
    # =====================================================

    discount_approval_status = fields.Selection(
        [
            ('none', 'No Approval Needed'),
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Discount Approval Status',
        default='none',
        readonly=True,
        copy=False,
    )

    discount_approval_user_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False,
    )

    requires_discount_approval = fields.Boolean(
        string='Requires Approval',
        compute='_compute_requires_discount_approval',
        store=True,
    )

    high_discount_reason = fields.Text(
        string='Discount Reason',
    )

    # =====================================================
    # COMPUTE
    # =====================================================

    @api.depends('order_line.discount')
    def _compute_requires_discount_approval(self):

        for order in self:

            order.requires_discount_approval = any(
                line.discount > 5
                for line in order.order_line
            )

    # =====================================================
    # RESET APPROVAL IF ORDER CHANGES
    # =====================================================

    def write(self, vals):

        result = super().write(vals)

        if 'order_line' in vals:

            for order in self:

                # Solo resetear si ya tenia un estado activo
                if order.discount_approval_status != 'none':

                    order.sudo().write({
                        'discount_approval_status': 'none',
                        'discount_approval_user_id': False,
                    })

        return result

    # =====================================================
    # VALIDATE BEFORE CONFIRM
    # =====================================================

    def _check_discount_approval(self):

        for order in self:

            if (
                order.requires_discount_approval
                and order.discount_approval_status != 'approved'
            ):

                raise exceptions.UserError(
                    _(
                        'Cannot confirm quotation.\n'
                        'Discounts greater than 5% '
                        'require supervisor approval.'
                    )
                )

    # =====================================================
    # CONFIRM ORDER
    # =====================================================

    def action_confirm(self):

        self._check_discount_approval()

        return super().action_confirm()

    # =====================================================
    # REQUEST APPROVAL
    # =====================================================

    def action_request_discount_approval(self):

        for order in self:

            if not order.requires_discount_approval:

                raise exceptions.UserError(
                    _('This quotation does not require approval.')
                )

            if order.discount_approval_status == 'approved':

                raise exceptions.UserError(
                    _('This quotation is already approved.')
                )

            supervisor = order._get_approval_user()

            order.discount_approval_status = 'pending'

            self.env['mail.activity'].create({

                'activity_type_id': self.env.ref(
                    'mail.mail_activity_data_todo'
                ).id,

                'summary': _('Discount Approval'),

                'note': _(
                    'Discount approval requested for quotation %s'
                ) % order.name,

                'user_id': supervisor.id,

                'res_id': order.id,

                'res_model_id': self.env['ir.model']._get_id(
                    'sale.order'
                ),
            })

    # =====================================================
    # GET SUPERVISOR
    # =====================================================

    def _get_approval_user(self):

        group = self.env.ref(
            'sale_discount_approval.group_sale_discount_supervisor',
            raise_if_not_found=False,
        )

        if not group:

            raise exceptions.UserError(
                _('Supervisor group not found.')
            )

        users = group.users.filtered(
            lambda u: not u.share
        )

        if not users:

            raise exceptions.UserError(
                _('No supervisor found for approval.')
            )

        return users[0]

    # =====================================================
    # APPROVE
    # =====================================================

    def action_approve_discount(self):

        if not self.env.user.has_group(
            'sale_discount_approval.group_sale_discount_supervisor'
        ):

            raise exceptions.UserError(
                _('Only supervisors can approve discounts.')
            )

        for order in self:

            if order.discount_approval_status != 'pending':

                raise exceptions.UserError(
                    _('Only pending requests can be approved.')
                )

            order.discount_approval_status = 'approved'

            order.discount_approval_user_id = self.env.user.id

    # =====================================================
    # REJECT
    # =====================================================

    def action_reject_discount(self):

        if not self.env.user.has_group(
            'sale_discount_approval.group_sale_discount_supervisor'
        ):

            raise exceptions.UserError(
                _('Only supervisors can reject discounts.')
            )

        for order in self:

            if order.discount_approval_status != 'pending':

                raise exceptions.UserError(
                    _('Only pending requests can be rejected.')
                )

            order.discount_approval_status = 'rejected'

            order.discount_approval_user_id = self.env.user.id

    # =====================================================
    # RESET APPROVAL
    # =====================================================

    def action_reset_discount_approval(self):

        for order in self:

            order.discount_approval_status = 'none'

            order.discount_approval_user_id = False