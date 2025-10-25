# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VisaDocument(models.Model):
    _name = 'visa.document'
    _description = 'Document Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Document Name', required=True)
    student_id = fields.Many2one('visa.student', string='Student', required=True, ondelete='cascade')
    application_id = fields.Many2one('visa.application', string='Application', ondelete='cascade')

    # Document Details
    document_type = fields.Selection([
        ('passport', 'Passport'),
        ('photo', 'Photograph'),
        ('10th_certificate', '10th Certificate'),
        ('12th_certificate', '12th Certificate'),
        ('bachelor_certificate', 'Bachelor Certificate'),
        ('bachelor_marksheet', 'Bachelor Marksheet'),
        ('master_certificate', 'Master Certificate'),
        ('master_marksheet', 'Master Marksheet'),
        ('english_test', 'English Test Certificate'),
        ('sop', 'Statement of Purpose'),
        ('lor', 'Letter of Recommendation'),
        ('resume', 'Resume/CV'),
        ('work_experience', 'Work Experience Letter'),
        ('bank_statement', 'Bank Statement'),
        ('affidavit', 'Affidavit'),
        ('police_clearance', 'Police Clearance'),
        ('medical_certificate', 'Medical Certificate'),
        ('other', 'Other')
    ], string='Document Type', required=True, tracking=True)

    # File Upload
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    file_name = fields.Char(string='File Name')

    # Status
    state = fields.Selection([
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending', tracking=True)

    # Dates
    submission_date = fields.Date(string='Submission Date')
    verification_date = fields.Date(string='Verification Date')
    expiry_date = fields.Date(string='Expiry Date')

    # Verification
    verified_by = fields.Many2one('res.users', string='Verified By')
    rejection_reason = fields.Text(string='Rejection Reason')

    # Flags
    is_mandatory = fields.Boolean(string='Mandatory', default=True)
    is_expired = fields.Boolean(string='Expired', compute='_compute_is_expired', store=True)

    notes = fields.Text(string='Notes')

    @api.depends('expiry_date')
    def _compute_is_expired(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_expired = rec.expiry_date and rec.expiry_date < today

    def action_receive(self):
        self.write({
            'state': 'received',
            'submission_date': fields.Date.today()
        })

    def action_verify(self):
        self.write({
            'state': 'verified',
            'verification_date': fields.Date.today(),
            'verified_by': self.env.user.id
        })

    def action_reject(self):
        self.state = 'rejected'

    def action_reset(self):
        self.state = 'pending'