# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VisaApplication(models.Model):
    _name = 'visa.application'
    _description = 'Visa Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(string='Application Number', required=True, copy=False, readonly=True, default='New')
    student_id = fields.Many2one('visa.student', string='Student', required=True, tracking=True)
    student_email = fields.Char(related='student_id.email', string='Student Email', store=True)
    student_phone = fields.Char(related='student_id.phone', string='Student Phone', store=True)

    # University & Course
    university_id = fields.Many2one('visa.university', string='University', required=True, tracking=True)
    course_id = fields.Many2one('visa.course', string='Course', domain="[('university_id', '=', university_id)]",
                                tracking=True)
    intake = fields.Selection([
        ('january', 'January'),
        ('february', 'February'),
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December')
    ], string='Intake', required=True)
    intake_year = fields.Char(string='Intake Year', required=True)

    # Application Details
    application_date = fields.Date(string='Application Date', default=fields.Date.today, required=True)
    submission_date = fields.Date(string='Submission Date')
    university_response_date = fields.Date(string='University Response Date')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('document_collection', 'Document Collection'),
        ('document_verification', 'Document Verification'),
        ('submitted', 'Submitted to University'),
        ('in_progress', 'In Progress'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('visa_filed', 'Visa Filed'),
        ('visa_approved', 'Visa Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # Consultant
    consultant_id = fields.Many2one('visa.consultant', string='Assigned Consultant', tracking=True)

    # Financial
    service_fee = fields.Monetary(string='Service Fee', currency_field='currency_id')
    university_fee = fields.Monetary(string='University Application Fee', currency_field='currency_id')
    total_fee = fields.Monetary(string='Total Fee', compute='_compute_total_fee', store=True,
                                currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Relations
    document_ids = fields.One2many('visa.document', 'application_id', string='Documents')
    payment_ids = fields.One2many('visa.payment', 'application_id', string='Payments')

    # Outcome
    outcome = fields.Selection([
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted')
    ], string='Outcome', default='pending')
    rejection_reason = fields.Text(string='Rejection Reason')

    # Priority
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'High'),
        ('2', 'Very High')
    ], string='Priority', default='0')

    # Notes
    notes = fields.Text(string='Notes')

    # Computed Fields
    document_count = fields.Integer(string='Documents', compute='_compute_document_count')
    payment_count = fields.Integer(string='Payments', compute='_compute_payment_count')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('visa.application') or 'New'
        return super(VisaApplication, self).create(vals)

    @api.depends('service_fee', 'university_fee')
    def _compute_total_fee(self):
        for rec in self:
            rec.total_fee = rec.service_fee + rec.university_fee

    @api.depends('document_ids')
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = len(rec.payment_ids)

    def action_submit(self):
        if not self.document_ids:
            raise UserError(_('Please add documents before submitting the application!'))
        self.write({
            'state': 'document_verification',
            'submission_date': fields.Date.today()
        })

    def action_verify_documents(self):
        incomplete_docs = self.document_ids.filtered(lambda d: d.state != 'verified')
        if incomplete_docs:
            raise UserError(_('Please verify all documents before proceeding!'))
        self.state = 'submitted'

    def action_submit_to_university(self):
        self.state = 'in_progress'

    def action_offer_received(self):
        self.write({
            'state': 'offer_received',
            'university_response_date': fields.Date.today()
        })

    def action_accept_offer(self):
        self.state = 'offer_accepted'

    def action_file_visa(self):
        self.state = 'visa_filed'

    def action_visa_approved(self):
        self.write({
            'state': 'visa_approved',
            'outcome': 'accepted'
        })
        self.student_id.state = 'completed'

    def action_reject(self):
        self.write({
            'state': 'rejected',
            'outcome': 'rejected'
        })

    def action_cancel(self):
        self.state = 'cancelled'

    def action_set_draft(self):
        self.state = 'draft'

    def action_view_documents(self):
        return {
            'name': _('Documents'),
            'view_mode': 'tree,form',
            'res_model': 'visa.document',
            'type': 'ir.actions.act_window',
            'domain': [('application_id', '=', self.id)],
            'context': {'default_application_id': self.id, 'default_student_id': self.student_id.id}
        }

    def action_view_payments(self):
        return {
            'name': _('Payments'),
            'view_mode': 'tree,form',
            'res_model': 'visa.payment',
            'type': 'ir.actions.act_window',
            'domain': [('application_id', '=', self.id)],
            'context': {'default_application_id': self.id, 'default_student_id': self.student_id.id}
        }

    @api.onchange('university_id')
    def _onchange_university_id(self):
        self.course_id = False
        return {
            'domain': {
                'course_id': [('university_id', '=', self.university_id.id)]
            }
        }