# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


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
    # invoice_id = fields.Many2one('account.move', string='Invoice')

    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('visa.payment') or 'New'
        return super(VisaPayment, self).create(vals)

    def action_confirm(self):
        self.state = 'pending'

    def action_paid(self):
        self.state = 'paid'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_reset_draft(self):
        self.state = 'draft'