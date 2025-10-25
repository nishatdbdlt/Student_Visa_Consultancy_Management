# -*- coding: utf-8 -*-
# from odoo import http


# class StudentVisaConsultancyManagement(http.Controller):
#     @http.route('/student__visa__consultancy__management/student__visa__consultancy__management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/student__visa__consultancy__management/student__visa__consultancy__management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('student__visa__consultancy__management.listing', {
#             'root': '/student__visa__consultancy__management/student__visa__consultancy__management',
#             'objects': http.request.env['student__visa__consultancy__management.student__visa__consultancy__management'].search([]),
#         })

#     @http.route('/student__visa__consultancy__management/student__visa__consultancy__management/objects/<model("student__visa__consultancy__management.student__visa__consultancy__management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('student__visa__consultancy__management.object', {
#             'object': obj
#         })

