# -*- coding: utf-8 -*-

from odoo import models, api, _, fields


class AccountBillingNote(models.Model):
    _name = 'account.billing.note'
    _inherit = ['mail.thread']
    _description = "Account Billing Note"
    _order = 'id desc,date desc'

    @api.onchange('partner_id')
    def _onchange_partner(self):
        val = []

        account_invoice = self.env['account.move']

        invoice_line = account_invoice.search([
            ('partner_id', '=', self.partner_id.id),
            ('state', 'in', ['draft']),
            ('move_type', 'in', ['out_invoice', 'out_refund'])
        ], order='invoice_date asc')

        for invoice in invoice_line:
            wht_total = sum([x.wt_tax_id.amount for x in invoice.invoice_line_ids]) or 0.0
            if not invoice.blling_ids:
                val.append((0,0,{
                    'invoice_id': invoice.id,
                    'date_invoice': invoice.invoice_date,
                    'due_date': invoice.invoice_date_due,
                    'amount': invoice.move_type == 'out_refund' and -invoice.amount_total or invoice.amount_total,
                    'wht_total': wht_total,
                    'balance': invoice.move_type == 'out_refund' and -invoice.amount_residual or invoice.amount_residual,
                    'payment_term_id': invoice.invoice_payment_term_id.id,
                    'paid_amount': invoice.move_type == 'out_refund' and -invoice.amount_residual or invoice.amount_residual,
                }))

        return {'value': {'line_ids': val, 'billing_term_id': self.partner_id.property_payment_term_id.id}}

    def _compute_amount(self):
        for billing in self:
            billing.amount_billing = sum(line.paid_amount for line in billing.line_ids)
            billing.amount_wht = sum(line.wht_total for line in billing.line_ids)

    number = fields.Char(
        string="Number",
        required=False,
        readonly=True,
    )
    date = fields.Date(
        string="Date Billing",
        required=False,
        default=fields.Date.today(),
        track_visibility='onchange',
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        track_visibility='onchange',
    )
    note = fields.Text(
        string="Note",
        required=False,
    )
    line_ids = fields.One2many(
        comodel_name="account.billing.note.line",
        inverse_name="billing_id",
        string="Detail",
        required=False,
    )
    billing_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Term",
        track_visibility='onchange',
        required=False,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ('draft', 'Draft'),
            ('open', 'Open'),
            ('approve', 'Approve'),
            ('cancel', 'Cancel')
        ],
        required=False,
        default='draft',
        track_visibility='onchange',
    )
    amount_billing = fields.Float(
        compute="_compute_amount",
        string="Amount",
        track_visibility='onchange'
    )
    amount_wht = fields.Float(
        compute="_compute_amount",
        string="WHT Amount",
        track_visibility='onchange'
    )

    def name_get(self):
        return [(billing.id, billing.number) for billing in self]

    def action_open(self):
        for billing in self:
            if billing.number is False:
                billing.number = self.env['ir.sequence'].next_by_code('billing.note')
            billing.state = 'open'
        return True

    def action_cancel(self):
        for billing in self:
            billing.state = 'cancel'
        return True

    def set_to_draft(self):
        for billing in self:
            billing.state = 'draft'
        return True

    def action_approve(self):
        for billing in self:
            billing.state = 'approve'
        return True

    def create_payment_order(self):
        """docstring for create_payment_order"""
        moves = self.env['account.move']
        for line in self.line_ids:
            moves |= line.invoice_id
        if moves:
            action = moves.create_account_payment_line()
            return action

    def create_draft_payment(self):
        vals = []
        account_journal = self.env['account.journal'].search([('type', 'in', ['cash', 'bank'])], limit=1)
        for billing in self:
            for line in billing.line_ids:
                wht_total = sum([x.wt_tax_id.amount for x in line.invoice_id.invoice_line_ids]) or 0.0
                vals.append([0, 0, {
                    'invoice_id': line.invoice_id.id,
                    'dute_date': line.due_date,
                    'amount': line.invoice_id.amount_total,
                    'wht_total': wht_total,
                    'balance': line.invoice_id.amount_residual,
                    'paid_amount': line.paid_amount,
                }])
            account_payment_obj = self.env['account.payment']
            payment_id = account_payment_obj.create({
                'payment_type': 'inbound',
                'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                'date': fields.Date.today(),
                'partner_id': billing.partner_id.id,
                'ref': billing.number,
                'journal_id': account_journal.id,
                # 'invoice_line': vals,
                'amount': billing.amount_billing,
                'state': 'draft',
                'partner_type': 'customer',

            })
        imd = self.env['ir.model.data']
        # action = imd._xmlid_to_obj('account.action_account_payments')
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_payments')
        form_view_id = imd._xmlid_to_res_id('account.view_account_payment_form')

        return {
            'name': action['name'],
            'type': action['type'],
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'views': [(form_view_id, 'form')],
            'target': 'news',
            'context': action['context'],
            'res_model': action['res_model'],
            'res_id': payment_id.id,
        }


class AccountBillingLine(models.Model):
    _name = 'account.billing.note.line'

    billing_id = fields.Many2one(
        comodel_name="account.billing.note",
        string="Billing Note",
        required=False,
    )
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        required=False,
    )
    date_invoice = fields.Date(
        string="Date Invoice",
        readonly=False,
    )
    due_date = fields.Date(
        string="Due Date",
        readonly=False,
    )
    amount = fields.Float(
        string='Amount',
        readonly=False,
    )
    balance = fields.Float(
        string='Balance',
        readonly=False,
    )
    wht_total = fields.Float(
        string='WHT',
        readonly=False,
    )
    paid_amount = fields.Float(
        strint='Paid Amount',
    )
    payment_term_id = fields.Many2one(
        comodel_name="account.payment.term",
        string="Term",
        required=False,
    )

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        invoice = self.invoice_id
        wht_total = sum([x.wt_tax_id.amount for x in invoice.invoice_line_ids]) or 0.0
        self.date_invoice = invoice.invoice_date
        self.due_date = invoice.invoice_date_due
        self.amount = invoice.amount_total
        self.balance = invoice.amount_residual
        self.wht_total = wht_total
        self.payment_term_id = invoice.invoice_payment_term_id.id
        self.paid_amount = invoice.amount_residual

    def check_billing_full(self):
        self.paid_amount = self.balance


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_billings(self):
        self.ensure_one()
        billing_ids = []
        billing = self.env['account.billing.note.line'].search([('invoice_id', '=', self.id)
                                                              , ('billing_id.state', '!=', 'cancel')
                                                           ])
        for bill in billing:
            billing_ids.append(bill.billing_id.id)
        if len(billing_ids) > 0:
            self.blling_ids = billing_ids
        else:
            self.blling_ids = None

    blling_ids = fields.One2many(
        comodel_name="account.billing.note",
        string="Billing Note",
        compute='_get_billings',
        required=False,
    )
