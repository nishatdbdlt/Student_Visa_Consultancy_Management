# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VisaInvoice(models.Model):
    _name = 'visa.invoice'
    _description = 'Visa Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'invoice_date desc'

    name = fields.Char(string='Invoice Number', required=True, copy=False, readonly=True, default='New')
    student_id = fields.Many2one('visa.student', string='Student', required=True, tracking=True)
    application_id = fields.Many2one('visa.application', string='Application')
    payment_id = fields.Many2one('visa.payment', string='Payment')

    # Invoice Details
    invoice_date = fields.Date(string='Invoice Date', default=fields.Date.today, required=True, tracking=True)
    due_date = fields.Date(string='Due Date', tracking=True)

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # Invoice Lines
    line_ids = fields.One2many('visa.invoice.line', 'invoice_id', string='Invoice Lines')

    # Amounts
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_amounts', store=True, currency_field='currency_id')
    tax_amount = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True,
                                 currency_field='currency_id')
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_amounts', store=True,
                                   currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Company Info
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    # Notes
    notes = fields.Text(string='Terms and Conditions')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('visa.invoice') or 'New'
        return super(VisaInvoice, self).create(vals)

    @api.depends('line_ids.subtotal', 'line_ids.tax_amount')
    def _compute_amounts(self):
        for invoice in self:
            subtotal = sum(invoice.line_ids.mapped('subtotal'))
            tax_amount = sum(invoice.line_ids.mapped('tax_amount'))
            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.total_amount = subtotal + tax_amount

    def action_send(self):
        """Mark invoice as sent"""
        self.state = 'sent'

    def action_mark_paid(self):
        """Mark invoice as paid"""
        self.state = 'paid'
        # Update related payment if exists
        if self.payment_id:
            self.payment_id.action_paid()

    def action_cancel(self):
        """Cancel invoice"""
        self.state = 'cancelled'

    def action_reset_draft(self):
        """Reset to draft"""
        self.state = 'draft'

    def action_print_invoice(self):
        """Print invoice report"""
        return self.env.ref('student__visa__consultancy__management.action_report_visa_invoice').report_action(self)


class VisaInvoiceLine(models.Model):
    _name = 'visa.invoice.line'
    _description = 'Visa Invoice Line'
    _order = 'sequence, id'

    invoice_id = fields.Many2one('visa.invoice', string='Invoice', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)

    # Product/Service Details
    description = fields.Char(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    unit_price = fields.Monetary(string='Unit Price', required=True, currency_field='currency_id')

    # Tax
    tax_percentage = fields.Float(string='Tax %', default=0.0)

    # Computed Amounts
    subtotal = fields.Monetary(string='Subtotal', compute='_compute_amounts', store=True, currency_field='currency_id')
    tax_amount = fields.Monetary(string='Tax Amount', compute='_compute_amounts', store=True,
                                 currency_field='currency_id')
    total = fields.Monetary(string='Total', compute='_compute_amounts', store=True, currency_field='currency_id')

    currency_id = fields.Many2one('res.currency', related='invoice_id.currency_id', string='Currency')

    @api.depends('quantity', 'unit_price', 'tax_percentage')
    def _compute_amounts(self):
        for line in self:
            subtotal = line.quantity * line.unit_price
            tax_amount = subtotal * (line.tax_percentage / 100)
            line.subtotal = subtotal
            line.tax_amount = tax_amount
            line.total = subtotal + tax_amount