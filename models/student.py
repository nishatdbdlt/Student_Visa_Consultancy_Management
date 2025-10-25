# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VisaStudent(models.Model):
    _name = 'visa.student'
    _description = 'Student Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Full Name', required=True, tracking=True)
    email = fields.Char(string='Email', required=True, tracking=True)
    phone = fields.Char(string='Phone', required=True, tracking=True)
    mobile = fields.Char(string='Mobile')
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', tracking=True)

    # Address Information
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP Code')
    country_id = fields.Many2one('res.country', string='Country')

    # Passport Information
    passport_number = fields.Char(string='Passport Number', tracking=True)
    passport_issue_date = fields.Date(string='Passport Issue Date')
    passport_expiry_date = fields.Date(string='Passport Expiry Date')
    passport_country_id = fields.Many2one('res.country', string='Passport Country')

    # Educational Background
    highest_qualification = fields.Selection([
        ('10th', '10th Grade'),
        ('12th', '12th Grade'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('phd', 'PhD')
    ], string='Highest Qualification')
    percentage = fields.Float(string='Percentage/CGPA')
    year_of_passing = fields.Char(string='Year of Passing')

    # English Test Scores
    english_test = fields.Selection([
        ('ielts', 'IELTS'),
        ('toefl', 'TOEFL'),
        ('pte', 'PTE'),
        ('duolingo', 'Duolingo'),
        ('none', 'None')
    ], string='English Test', default='none')
    overall_score = fields.Float(string='Overall Score')
    test_date = fields.Date(string='Test Date')

    # Relations
    application_ids = fields.One2many('visa.application', 'student_id', string='Applications')
    document_ids = fields.One2many('visa.document', 'student_id', string='Documents')
    payment_ids = fields.One2many('visa.payment', 'student_id', string='Payments')
    consultant_id = fields.Many2one('visa.consultant', string='Assigned Consultant', tracking=True)

    # Status
    state = fields.Selection([
        ('inquiry', 'Inquiry'),
        ('registered', 'Registered'),
        ('in_process', 'In Process'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='inquiry', tracking=True)

    # Computed Fields
    application_count = fields.Integer(string='Applications', compute='_compute_application_count')
    document_count = fields.Integer(string='Documents', compute='_compute_document_count')
    total_paid = fields.Monetary(string='Total Paid', compute='_compute_total_paid', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Notes
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('email_unique', 'unique(email)', 'Email must be unique!'),
        ('passport_unique', 'unique(passport_number)', 'Passport number must be unique!')
    ]

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                today = fields.Date.today()
                rec.age = today.year - rec.date_of_birth.year - (
                            (today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day))
            else:
                rec.age = 0

    @api.depends('application_ids')
    def _compute_application_count(self):
        for rec in self:
            rec.application_count = len(rec.application_ids)

    @api.depends('document_ids')
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids)

    @api.depends('payment_ids.amount', 'payment_ids.state')
    def _compute_total_paid(self):
        for rec in self:
            paid_payments = rec.payment_ids.filtered(lambda p: p.state == 'paid')
            rec.total_paid = sum(paid_payments.mapped('amount'))

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and '@' not in rec.email:
                raise ValidationError(_('Please enter a valid email address!'))

    @api.constrains('passport_expiry_date')
    def _check_passport_expiry(self):
        for rec in self:
            if rec.passport_expiry_date and rec.passport_expiry_date < fields.Date.today():
                raise ValidationError(_('Passport has expired!'))

    def action_set_registered(self):
        self.state = 'registered'

    def action_set_in_process(self):
        self.state = 'in_process'

    def action_set_completed(self):
        self.state = 'completed'

    def action_view_applications(self):
        return {
            'name': _('Applications'),
            'view_mode': 'tree,form',
            'res_model': 'visa.application',
            'type': 'ir.actions.act_window',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id}
        }

    def action_view_documents(self):
        return {
            'name': _('Documents'),
            'view_mode': 'tree,form',
            'res_model': 'visa.document',
            'type': 'ir.actions.act_window',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id}
        }