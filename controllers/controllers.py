# -*- coding: utf-8 -*-

from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import json


class VisaPortalController(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'student_count' in counters:
            values['student_count'] = request.env['visa.student'].search_count([])
        if 'application_count' in counters:
            values['application_count'] = request.env['visa.application'].search_count([])
        if 'document_count' in counters:
            values['document_count'] = request.env['visa.document'].search_count([])
        if 'payment_count' in counters:
            values['payment_count'] = request.env['visa.payment'].search_count([])
        return values

    # ==================== DASHBOARD ====================
    @http.route(['/my/visa/dashboard'], type='http', auth='user', website=True)
    def visa_dashboard(self, **kwargs):
        """Main Dashboard with all statistics"""
        dashboard = request.env['visa.dashboard'].sudo().search([], limit=1)
        if not dashboard:
            dashboard = request.env['visa.dashboard'].sudo().create({'name': 'Dashboard'})

        values = {
            'page_name': 'visa_dashboard',
            'dashboard': dashboard,
            'total_students': dashboard.total_students,
            'total_applications': dashboard.total_applications,
            'total_revenue': dashboard.total_revenue,
            'pending_documents': dashboard.pending_documents,
            'overdue_payments': dashboard.overdue_payments,
            'students_this_month': dashboard.students_this_month,
            'applications_this_month': dashboard.applications_this_month,
            'revenue_this_month': dashboard.revenue_this_month,
            'success_rate': dashboard.success_rate,
            'draft_applications': dashboard.draft_applications,
            'in_progress_applications': dashboard.in_progress_applications,
            'approved_applications': dashboard.approved_applications,
            'rejected_applications': dashboard.rejected_applications,
        }
        return request.render('student__visa__consultancy__management.portal_visa_dashboard', values)

    # ==================== STUDENTS ====================
    @http.route(['/my/visa/students', '/my/visa/students/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_students(self, page=1, search='', sortby=None, filterby=None, **kwargs):
        """List all students with search and filter"""
        Student = request.env['visa.student']

        domain = []
        if search:
            domain += ['|', '|', ('name', 'ilike', search), ('email', 'ilike', search), ('phone', 'ilike', search)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        student_count = Student.search_count(domain)
        pager = portal_pager(
            url="/my/visa/students",
            url_args={'sortby': sortby, 'search': search},
            total=student_count,
            page=page,
            step=20
        )

        students = Student.search(domain, order=order, limit=20, offset=pager['offset'])

        values = {
            'page_name': 'students',
            'students': students,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'search': search,
        }
        return request.render('student__visa__consultancy__management.portal_my_students', values)

    @http.route(['/my/visa/student/<int:student_id>'], type='http', auth='user', website=True)
    def portal_student_detail(self, student_id, **kwargs):
        """View single student details"""
        try:
            student = request.env['visa.student'].browse(student_id)
            if not student.exists():
                return request.redirect('/my/visa/students')

            values = {
                'page_name': 'student_detail',
                'student': student,
            }
            return request.render('student__visa__consultancy__management.portal_student_detail', values)
        except (AccessError, MissingError):
            return request.redirect('/my/visa/students')

    @http.route(['/my/visa/student/create'], type='http', auth='user', website=True)
    def portal_student_create(self, **kwargs):
        """Create new student form"""
        countries = request.env['res.country'].search([])
        values = {
            'page_name': 'student_create',
            'countries': countries,
        }
        return request.render('student__visa__consultancy__management.portal_student_form', values)

    @http.route(['/my/visa/student/edit/<int:student_id>'], type='http', auth='user', website=True)
    def portal_student_edit(self, student_id, **kwargs):
        """Edit student form"""
        try:
            student = request.env['visa.student'].browse(student_id)
            if not student.exists():
                return request.redirect('/my/visa/students')

            countries = request.env['res.country'].search([])
            values = {
                'page_name': 'student_edit',
                'student': student,
                'countries': countries,
            }
            return request.render('student__visa__consultancy__management.portal_student_form', values)
        except (AccessError, MissingError):
            return request.redirect('/my/visa/students')

    @http.route(['/my/visa/student/save'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_student_save(self, **post):
        """Save student (create or update)"""
        student_id = post.get('student_id')

        vals = {
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'passport_number': post.get('passport_number'),
            'date_of_birth': post.get('date_of_birth'),
            'nationality_id': int(post.get('nationality_id')) if post.get('nationality_id') else False,
            'address': post.get('address'),
            'city': post.get('city'),
            'state': post.get('state'),
            'zip': post.get('zip'),
            'country_id': int(post.get('country_id')) if post.get('country_id') else False,
        }

        if student_id:
            student = request.env['visa.student'].browse(int(student_id))
            student.write(vals)
        else:
            student = request.env['visa.student'].create(vals)

        return request.redirect(f'/my/visa/student/{student.id}')

    @http.route(['/my/visa/student/delete/<int:student_id>'], type='http', auth='user', website=True, csrf=True)
    def portal_student_delete(self, student_id, **kwargs):
        """Delete student"""
        try:
            student = request.env['visa.student'].browse(student_id)
            if student.exists():
                student.unlink()
        except (AccessError, MissingError):
            pass
        return request.redirect('/my/visa/students')

    # ==================== APPLICATIONS ====================
    @http.route(['/my/visa/applications', '/my/visa/applications/page/<int:page>'], type='http', auth='user',
                website=True)
    def portal_my_applications(self, page=1, search='', sortby=None, filterby=None, **kwargs):
        """List all applications"""
        Application = request.env['visa.application']

        domain = []
        if search:
            domain += [('name', 'ilike', search)]

        if filterby and filterby != 'all':
            domain += [('state', '=', filterby)]

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'in_progress': {'label': _('In Progress'), 'domain': [('state', '=', 'in_progress')]},
            'visa_approved': {'label': _('Approved'), 'domain': [('state', '=', 'visa_approved')]},
            'rejected': {'label': _('Rejected'), 'domain': [('state', '=', 'rejected')]},
        }

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        if not filterby:
            filterby = 'all'

        order = searchbar_sortings[sortby]['order']

        application_count = Application.search_count(domain)
        pager = portal_pager(
            url="/my/visa/applications",
            url_args={'sortby': sortby, 'filterby': filterby, 'search': search},
            total=application_count,
            page=page,
            step=20
        )

        applications = Application.search(domain, order=order, limit=20, offset=pager['offset'])

        values = {
            'page_name': 'applications',
            'applications': applications,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'sortby': sortby,
            'filterby': filterby,
            'search': search,
        }
        return request.render('student__visa__consultancy__management.portal_my_applications', values)

    @http.route(['/my/visa/application/<int:application_id>'], type='http', auth='user', website=True)
    def portal_application_detail(self, application_id, **kwargs):
        """View application details"""
        try:
            application = request.env['visa.application'].browse(application_id)
            if not application.exists():
                return request.redirect('/my/visa/applications')

            values = {
                'page_name': 'application_detail',
                'application': application,
            }
            return request.render('student__visa__consultancy__management.portal_application_detail', values)
        except (AccessError, MissingError):
            return request.redirect('/my/visa/applications')

    @http.route(['/my/visa/application/create'], type='http', auth='user', website=True)
    def portal_application_create(self, **kwargs):
        """Create application form"""
        students = request.env['visa.student'].search([])
        countries = request.env['res.country'].search([])
        values = {
            'page_name': 'application_create',
            'students': students,
            'countries': countries,
        }
        return request.render('student__visa__consultancy__management.portal_application_form', values)

    @http.route(['/my/visa/application/edit/<int:application_id>'], type='http', auth='user', website=True)
    def portal_application_edit(self, application_id, **kwargs):
        """Edit application"""
        try:
            application = request.env['visa.application'].browse(application_id)
            if not application.exists():
                return request.redirect('/my/visa/applications')

            students = request.env['visa.student'].search([])
            countries = request.env['res.country'].search([])
            values = {
                'page_name': 'application_edit',
                'application': application,
                'students': students,
                'countries': countries,
            }
            return request.render('student__visa__consultancy__management.portal_application_form', values)
        except (AccessError, MissingError):
            return request.redirect('/my/visa/applications')

    @http.route(['/my/visa/application/save'], type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def portal_application_save(self, **post):
        """Save application"""
        application_id = post.get('application_id')

        vals = {
            'student_id': int(post.get('student_id')) if post.get('student_id') else False,
            'application_type': post.get('application_type'),
            'destination_country_id': int(post.get('destination_country_id')) if post.get(
                'destination_country_id') else False,
            'university_name': post.get('university_name'),
            'course_name': post.get('course_name'),
            'intake': post.get('intake'),
            'visa_type': post.get('visa_type'),
            'application_date': post.get('application_date'),
            'expected_travel_date': post.get('expected_travel_date'),
            'notes': post.get('notes'),
        }

        if application_id:
            application = request.env['visa.application'].browse(int(application_id))
            application.write(vals)
        else:
            application = request.env['visa.application'].create(vals)

        return request.redirect(f'/my/visa/application/{application.id}')

    @http.route(['/my/visa/application/delete/<int:application_id>'], type='http', auth='user', website=True, csrf=True)
    def portal_application_delete(self, application_id, **kwargs):
        """Delete application"""
        try:
            application = request.env['visa.application'].browse(application_id)
            if application.exists():
                application.unlink()
        except (AccessError, MissingError):
            pass
        return request.redirect('/my/visa/applications')

    # ==================== DOCUMENTS ====================
    @http.route(['/my/visa/documents', '/my/visa/documents/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_documents(self, page=1, search='', filterby=None, **kwargs):
        """List all documents"""
        Document = request.env['visa.document']

        domain = []
        if search:
            domain += [('name', 'ilike', search)]

        if filterby and filterby != 'all':
            domain += [('state', '=', filterby)]

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'pending': {'label': _('Pending'), 'domain': [('state', '=', 'pending')]},
            'received': {'label': _('Received'), 'domain': [('state', '=', 'received')]},
            'verified': {'label': _('Verified'), 'domain': [('state', '=', 'verified')]},
            'rejected': {'label': _('Rejected'), 'domain': [('state', '=', 'rejected')]},
        }

        if not filterby:
            filterby = 'all'

        document_count = Document.search_count(domain)
        pager = portal_pager(
            url="/my/visa/documents",
            url_args={'filterby': filterby, 'search': search},
            total=document_count,
            page=page,
            step=20
        )

        documents = Document.search(domain, order='create_date desc', limit=20, offset=pager['offset'])

        values = {
            'page_name': 'documents',
            'documents': documents,
            'pager': pager,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
            'search': search,
        }
        return request.render('student__visa__consultancy__management.portal_my_documents', values)

    @http.route(['/my/visa/document/<int:document_id>'], type='http', auth='user', website=True)
    def portal_document_detail(self, document_id, **kwargs):
        """View document details"""
        try:
            document = request.env['visa.document'].browse(document_id)
            if not document.exists():
                return request.redirect('/my/visa/documents')

            values = {
                'page_name': 'document_detail',
                'document': document,
            }
            return request.render('student__visa__consultancy__management.portal_document_detail', values)
        except (AccessError, MissingError):
            return request.redirect('/my/visa/documents')

    @http.route(['/my/visa/document/delete/<int:document_id>'], type='http', auth='user', website=True, csrf=True)
    def portal_document_delete(self, document_id, **kwargs):
        """Delete document"""
        try:
            document = request.env['visa.document'].browse(document_id)
            if document.exists():
                document.unlink()
        except (AccessError, MissingError):
            pass
        return request.redirect('/my/visa/documents')

    # ==================== PAYMENTS ====================
    @http.route(['/my/visa/payments', '/my/visa/payments/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_payments(self, page=1, search='', filterby=None, **kwargs):
        """List all payments"""
        Payment = request.env['visa.payment']

        domain = []
        if search:
            domain += [('name', 'ilike', search)]

        if filterby and filterby != 'all':
            domain += [('state', '=', filterby)]

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'pending': {'label': _('Pending'), 'domain': [('state', '=', 'pending')]},
            'paid': {'label': _('Paid'), 'domain': [('state', '=', 'paid')]},
            'cancelled': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancelled')]},
        }

        if not filterby:
            filterby = 'all'

        payment_count = Payment.search_count(domain)
        pager = portal_pager(
            url="/my/visa/payments",
            url_args={'filterby': filterby, 'search': search},
            total=payment_count,
            page=page,
            step=20
        )

        payments = Payment.search(domain, order='create_date desc', limit=20, offset=pager['offset'])

        values = {
            'page_name': 'payments',
            'payments': payments,
            'pager': pager,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
            'search': search,
        }
        return request.render('student__visa__consultancy__management.portal_my_payments', values)

    @http.route(['/my/visa/payment/<int:payment_id>'], type='http', auth='user', website=True)
    def portal_payment_detail(self, payment_id, **kwargs):
        """View payment details"""
        try:
            payment = request.env['visa.payment'].browse(payment_id)
            if not payment.exists():
                return request.redirect('/my/visa/payments')

            values = {
                'page_name': 'payment_detail',
                'payment': payment,
            }
            return request.render('student__visa__consultancy__management.portal_payment_detail', values)
        except (AccessError, MissingError):
            return request.redirect('/my/visa/payments')

    @http.route(['/my/visa/payment/delete/<int:payment_id>'], type='http', auth='user', website=True, csrf=True)
    def portal_payment_delete(self, payment_id, **kwargs):
        """Delete payment"""
        try:
            payment = request.env['visa.payment'].browse(payment_id)
            if payment.exists():
                payment.unlink()
        except (AccessError, MissingError):
            pass
        return request.redirect('/my/visa/payments')