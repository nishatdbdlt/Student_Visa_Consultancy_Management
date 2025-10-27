# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class VisaDashboard(models.Model):
    _name = 'visa.dashboard'
    _description = 'Visa Consultancy Dashboard'

    name = fields.Char(string='Dashboard', default='Dashboard')

    # Statistics
    total_students = fields.Integer(string='Total Students', compute='_compute_statistics')
    total_applications = fields.Integer(string='Total Applications', compute='_compute_statistics')
    total_revenue = fields.Monetary(string='Total Revenue', compute='_compute_statistics', currency_field='currency_id')
    pending_documents = fields.Integer(string='Pending Documents', compute='_compute_statistics')
    overdue_payments = fields.Integer(string='Overdue Payments', compute='_compute_statistics')

    # This Month
    students_this_month = fields.Integer(string='Students This Month', compute='_compute_statistics')
    applications_this_month = fields.Integer(string='Applications This Month', compute='_compute_statistics')
    revenue_this_month = fields.Monetary(string='Revenue This Month', compute='_compute_statistics',
                                         currency_field='currency_id')

    # Success Rate
    success_rate = fields.Float(string='Success Rate (%)', compute='_compute_statistics')

    # Applications by Status
    draft_applications = fields.Integer(string='Draft', compute='_compute_application_status')
    in_progress_applications = fields.Integer(string='In Progress', compute='_compute_application_status')
    approved_applications = fields.Integer(string='Approved', compute='_compute_application_status')
    rejected_applications = fields.Integer(string='Rejected', compute='_compute_application_status')

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    @api.depends()
    def _compute_statistics(self):
        for record in self:
            # Total counts
            record.total_students = self.env['visa.student'].search_count([])
            record.total_applications = self.env['visa.application'].search_count([])

            # Revenue calculation
            paid_payments = self.env['visa.payment'].search([('state', '=', 'paid')])
            record.total_revenue = sum(paid_payments.mapped('amount'))

            # Pending documents
            record.pending_documents = self.env['visa.document'].search_count([
                ('state', 'in', ['pending', 'received'])
            ])

            # Overdue payments
            today = fields.Date.today()
            record.overdue_payments = self.env['visa.payment'].search_count([
                ('due_date', '<', today),
                ('state', '!=', 'paid')
            ])

            # This month statistics
            first_day = today.replace(day=1)
            record.students_this_month = self.env['visa.student'].search_count([
                ('create_date', '>=', first_day)
            ])
            record.applications_this_month = self.env['visa.application'].search_count([
                ('create_date', '>=', first_day)
            ])

            month_payments = self.env['visa.payment'].search([
                ('payment_date', '>=', first_day),
                ('state', '=', 'paid')
            ])
            record.revenue_this_month = sum(month_payments.mapped('amount'))

            # Success rate
            total_completed = self.env['visa.application'].search_count([
                ('state', 'in', ['visa_approved', 'rejected'])
            ])
            approved = self.env['visa.application'].search_count([('state', '=', 'visa_approved')])
            record.success_rate = (approved / total_completed * 100) if total_completed > 0 else 0

    @api.depends()
    def _compute_application_status(self):
        for record in self:
            record.draft_applications = self.env['visa.application'].search_count([('state', '=', 'draft')])
            record.in_progress_applications = self.env['visa.application'].search_count([('state', '=', 'in_progress')])
            record.approved_applications = self.env['visa.application'].search_count([('state', '=', 'visa_approved')])
            record.rejected_applications = self.env['visa.application'].search_count([('state', '=', 'rejected')])

    def action_view_students(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'visa.student',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_view_applications(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Applications',
            'res_model': 'visa.application',
            'view_mode': 'kanban,tree,form',
            'target': 'current',
        }

    def action_view_pending_documents(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pending Documents',
            'res_model': 'visa.document',
            'view_mode': 'tree,form',
            'domain': [('state', 'in', ['pending', 'received'])],
            'target': 'current',
        }

    def action_view_overdue_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Overdue Payments',
            'res_model': 'visa.payment',
            'view_mode': 'tree,form',
            'domain': [('due_date', '<', fields.Date.today()), ('state', '!=', 'paid')],
            'target': 'current',
        }