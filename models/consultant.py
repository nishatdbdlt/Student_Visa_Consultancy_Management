# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VisaConsultant(models.Model):
    _name = 'visa.consultant'
    _description = 'Visa Consultant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Consultant Name', required=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Related User', tracking=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone', required=True)
    mobile = fields.Char(string='Mobile')

    # Employment Details
    employee_id = fields.Char(string='Employee ID')
    joining_date = fields.Date(string='Joining Date')
    department = fields.Char(string='Department')

    # Specialization
    specialization_country_ids = fields.Many2many('res.country', string='Specialization Countries')
    expertise_level = fields.Selection([
        ('junior', 'Junior'),
        ('senior', 'Senior'),
        ('expert', 'Expert')
    ], string='Expertise Level', default='junior')

    # Relations
    student_ids = fields.One2many('visa.student', 'consultant_id', string='Students')
    application_ids = fields.One2many('visa.application', 'consultant_id', string='Applications')

    # Status
    active = fields.Boolean(string='Active', default=True)

    # Performance Metrics
    total_students = fields.Integer(string='Total Students', compute='_compute_metrics', store=True)
    total_applications = fields.Integer(string='Total Applications', compute='_compute_metrics', store=True)
    success_rate = fields.Float(string='Success Rate (%)', compute='_compute_success_rate', store=True)

    notes = fields.Text(string='Notes')

    @api.depends('student_ids', 'application_ids')
    def _compute_metrics(self):
        for rec in self:
            rec.total_students = len(rec.student_ids)
            rec.total_applications = len(rec.application_ids)

    @api.depends('application_ids.state')
    def _compute_success_rate(self):
        for rec in self:
            total = len(rec.application_ids)
            if total > 0:
                approved = len(rec.application_ids.filtered(lambda a: a.state == 'visa_approved'))
                rec.success_rate = (approved / total) * 100
            else:
                rec.success_rate = 0.0

    def action_view_students(self):
        return {
            'name': _('Students'),
            'view_mode': 'tree,form',
            'res_model': 'visa.student',
            'type': 'ir.actions.act_window',
            'domain': [('consultant_id', '=', self.id)],
        }

    def action_view_applications(self):
        return {
            'name': _('Applications'),
            'view_mode': 'tree,form',
            'res_model': 'visa.application',
            'type': 'ir.actions.act_window',
            'domain': [('consultant_id', '=', self.id)],
        }