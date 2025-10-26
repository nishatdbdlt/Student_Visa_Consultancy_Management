# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VisaPayment(models.Model):
    _name = 'visa.payment'
    _description = 'Payment Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'payment_date desc'

    name = fields.Char(string='Payment Reference', required=True, copy=False, readonly=True, default='New')
    student_id = fields.Many2one('visa.student', string='Student', required=True, tracking=True)
    application_id = fields.Many2one('visa.application', string='Application', tracking=True)

    # Payment Details
    payment_type = fields.Selection([
        ('service_fee', 'Service Fee'),
        ('university_fee', 'University Application Fee'),
        ('document_fee', 'Document Fee'),
        ('visa_fee', 'Visa Fee'),
        ('other', 'Other')
    ], string='Payment Type', required=True, default='service_fee')

    amount = fields.Monetary(string='Amount', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Payment Method
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Credit/Debit Card'),
        ('cheque', 'Cheque'),
        ('online', 'Online Payment')
    ], string='Payment Method', required=True)

    # Dates
    payment_date = fields.Date(string='Payment Date', default=fields.Date.today, required=True)
    due_date = fields.Date(string='Due Date')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # Bank Details (for bank transfer)
    bank_name = fields.Char(string='Bank Name')
    transaction_id = fields.Char(string='Transaction ID')
    cheque_number = fields.Char(string='Cheque Number')

    # Invoice
    invoice_id = fields.Many2one('visa.invoice', string='Invoice', readonly=True)
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')

    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('visa.payment') or 'New'
        return super(VisaPayment, self).create(vals)

    @api.depends('invoice_id')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = 1 if rec.invoice_id else 0

    def action_confirm(self):
        """Confirm payment and generate invoice"""
        for payment in self:
            if not payment.invoice_id:
                payment._generate_invoice()
            payment.state = 'pending'

    def action_paid(self):
        """Mark payment as paid"""
        self.state = 'paid'
        # Mark invoice as paid
        if self.invoice_id:
            self.invoice_id.action_mark_paid()

    def action_cancel(self):
        self.state = 'cancelled'

    def action_reset_draft(self):
        self.state = 'draft'

    def _generate_invoice(self):
        """Automatically generate invoice for this payment"""
        self.ensure_one()

        # Get payment type description
        payment_type_dict = dict(self._fields['payment_type'].selection)
        description = payment_type_dict.get(self.payment_type, 'Service')

        # Create invoice
        invoice_vals = {
            'student_id': self.student_id.id,
            'application_id': self.application_id.id if self.application_id else False,
            'payment_id': self.id,
            'invoice_date': self.payment_date,
            'due_date': self.due_date,
            'state': 'draft',
            'notes': 'Payment for: ' + self.name,
        }

        invoice = self.env['visa.invoice'].create(invoice_vals)

        # Create invoice line
        line_vals = {
            'invoice_id': invoice.id,
            'description': description,
            'quantity': 1,
            'unit_price': self.amount,
            'tax_percentage': 0.0,  # You can add tax calculation if needed
        }

        self.env['visa.invoice.line'].create(line_vals)

        # Link invoice to payment
        self.invoice_id = invoice.id

        return invoice

    def action_view_invoice(self):
        """Open the related invoice"""
        self.ensure_one()
        return {
            'name': _('Invoice'),
            'view_mode': 'form',
            'res_model': 'visa.invoice',
            'res_id': self.invoice_id.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_generate_invoice(self):
        """Manual invoice generation button"""
        for payment in self:
            if payment.invoice_id:
                raise UserError(_('Invoice already exists for this payment!'))
            payment._generate_invoice()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Invoice generated successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }