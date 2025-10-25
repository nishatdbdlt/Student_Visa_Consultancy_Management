# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VisaUniversity(models.Model):
    _name = 'visa.university'
    _description = 'University Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='University Name', required=True, tracking=True)
    code = fields.Char(string='University Code')
    country_id = fields.Many2one('res.country', string='Country', required=True, tracking=True)
    city = fields.Char(string='City')
    website = fields.Char(string='Website')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')

    # University Details
    ranking = fields.Integer(string='World Ranking')
    type = fields.Selection([
        ('public', 'Public'),
        ('private', 'Private')
    ], string='Type')
    established_year = fields.Char(string='Established Year')

    # Requirements
    min_ielts = fields.Float(string='Minimum IELTS Score')
    min_toefl = fields.Float(string='Minimum TOEFL Score')
    min_percentage = fields.Float(string='Minimum Percentage')

    # Financial
    application_fee = fields.Monetary(string='Application Fee', currency_field='currency_id')
    tuition_fee_min = fields.Monetary(string='Tuition Fee (Min)', currency_field='currency_id')
    tuition_fee_max = fields.Monetary(string='Tuition Fee (Max)', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    # Relations
    course_ids = fields.One2many('visa.course', 'university_id', string='Courses')
    application_ids = fields.One2many('visa.application', 'university_id', string='Applications')

    # Status
    active = fields.Boolean(string='Active', default=True)
    is_partner = fields.Boolean(string='Partner University', default=False)

    # Computed
    course_count = fields.Integer(string='Courses', compute='_compute_course_count')
    application_count = fields.Integer(string='Applications', compute='_compute_application_count')

    # Notes
    description = fields.Html(string='Description')
    notes = fields.Text(string='Internal Notes')

    @api.depends('course_ids')
    def _compute_course_count(self):
        for rec in self:
            rec.course_count = len(rec.course_ids)

    @api.depends('application_ids')
    def _compute_application_count(self):
        for rec in self:
            rec.application_count = len(rec.application_ids)

    def action_view_courses(self):
        return {
            'name': _('Courses'),
            'view_mode': 'tree,form',
            'res_model': 'visa.course',
            'type': 'ir.actions.act_window',
            'domain': [('university_id', '=', self.id)],
            'context': {'default_university_id': self.id}
        }


class VisaCourse(models.Model):
    _name = 'visa.course'
    _description = 'University Course'
    _rec_name = 'name'

    name = fields.Char(string='Course Name', required=True)
    code = fields.Char(string='Course Code')
    university_id = fields.Many2one('visa.university', string='University', restore=True, ondelete='cascade')

    # Course Details
    level = fields.Selection([
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD')
    ], string='Level', required=True)
    duration = fields.Char(string='Duration (Years)')
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
    ], string='Main Intake')

    # Requirements
    required_percentage = fields.Float(string='Required Percentage')
    required_ielts = fields.Float(string='Required IELTS')

    # Financial
    tuition_fee = fields.Monetary(string='Tuition Fee', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='university_id.currency_id', string='Currency')

    # Status
    active = fields.Boolean(string='Active', default=True)

    description = fields.Text(string='Description')