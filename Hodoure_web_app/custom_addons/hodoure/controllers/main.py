# -*- coding: utf-8 -*-
import base64
import json
import math
from urllib.parse import parse_qs
from odoo import http, _
from odoo.http import request
from .common import valid_response, invalid_response, validate_token
import logging
import traceback

_logger = logging.getLogger(__name__)


class SchoolAPIController(http.Controller):
    
    @validate_token
    @http.route("/api/statistics", methods=["GET"], type="http", cors="*", auth="none", csrf=False)
    def get_statistics(self):
        try:
            user = request.env.user
            subjects = request.env['hodoure.subject'].sudo().search([('school_id', '=', user.school_id.id)])
            return valid_response({"statistics": 
                {
                 "nbr_students": len(user.teacher_id.class_ids.mapped('student_ids')),
                 "nbr_classes": len(user.teacher_id.class_ids),
                 "nbr_subjects": len(subjects),
                } 
            }, 200, "User statistics retrieved successfully")
        except Exception as error:
            _logger.error(_('Error while getting statistics') + str(error))
            traceback.print_exc()
            return invalid_response(error, 500)

    @validate_token
    @http.route("/api/teachers", methods=["GET"], type="http", cors="*", auth="none", csrf=False)
    def get_teachers(self):
        try:
            user = request.env.user
            return valid_response({"teacher": 
                {
                "id": user.teacher_id.id,
                "name": user.teacher_id.name,
                "phone": user.login,
                } 
            }, 200, "Teacher retrieved successfully")
        except Exception as error:
            _logger.error(_('Error while getting statistics') + str(error))
            traceback.print_exc()
            return invalid_response(error, 500)

    @validate_token
    @http.route("/api/classes", methods=["GET"], type="http", cors="*", auth="none", csrf=False)
    def get_classes(self):
        try:
            user = request.env.user
            return valid_response({"classes": [
                {
                 "id": classe.id, 
                 "name": classe.name
                 } for classe in user.teacher_id.class_ids
            ]
            }, 200,  "Classes retrieved successfully")
        except Exception as error:
            _logger.error(_('Error while getting classes') + str(error))
            traceback.print_exc()
            return invalid_response(error, 500)

    @validate_token
    @http.route('/api/students/<int:class_id>', type='http', auth='none', methods=['GET'], csrf=False, cors="*")
    def get_student_by_class(self, class_id, **kw):
        try:
            students = request.env['hodoure.student'].sudo().search([('class_id', '=', class_id)])
            result = [{                    
                "id": student.id,
                "name": student.name,
                "student_number": student.student_number,
                "image": base64.b64encode(student.image).decode('utf-8') if student.image else None,
                "class_name": student.class_name,
                "parent_name": student.parent_name,
                "parent_phone": student.parent_phone
                } for student in students]
            return valid_response({"students": result}, 200)
        except Exception as error:
            _logger.error(_('Error while getting students') + str(error))
            traceback.print_exc()
            return invalid_response(error, 500)

    @validate_token
    @http.route('/api/absence', type='http', auth='none', methods=['POST'], csrf=False, cors="*")
    def post_absence(self, **kw):
        args = request.httprequest.data.decode()
        try:
            user = request.env.user
            data = json.loads(args)
            if not data:
                return invalid_response("Missing data", 400)

            absence = request.env['hodoure.absence'].sudo().create({
                "period_id": data.get("period_id"),
                "class_id": data.get("class_id"),
                "subject_id": data.get("subject_id"),
                "teacher_id": user.teacher_id.id,
                "absent_student_ids": [(6, 0, data.get("absent_student_ids", []))]
            })

            return valid_response({"attendance_id": absence.id}, 200)
        except Exception as error:
            _logger.error(_('Error while posting absence') + str(error))
            traceback.print_exc()
            return invalid_response(error, 500)

    @validate_token
    @http.route("/api/subjects", methods=["GET"], type="http", cors="*", auth="none", csrf=False)
    def get_subjects(self):
        try:
            user = request.env.user
            subjects = request.env['hodoure.subject'].sudo().search([('school_id', '=', user.school_id.id)])
            return valid_response({"subjects": [
                {
                 "id": subject.id, 
                 "name": subject.name
                 } for subject in subjects
            ]
            }, 200, )
        except Exception as error:
            _logger.error(_('Error while getting subjects') + str(error))
            traceback.print_exc()
            return invalid_response(error, 500)

    @validate_token
    @http.route("/api/periods", methods=["GET"], type="http", cors="*", auth="none", csrf=False)
    def get_periods(self):
        try:
            user = request.env.user
            periods = request.env['hodoure.period'].sudo().search([('school_id', '=', user.school_id.id)])
            return valid_response({"periods": [
                {
                 "id": period.id, 
                 "name": period.name
                 } for period in periods
            ]
            }, 200, )
        except Exception as error:
            _logger.error(_('Error while getting periods') + str(error))
            traceback.print_exc()
            return invalid_response(error, 500)

    @validate_token
    @http.route("/api/students", methods=["GET"], type="http", cors="*", auth="none", csrf=False)
    def get_students(self):
        try:
            user = request.env.user
            students = request.env['hodoure.student'].sudo().search([('school_id', '=', user.school_id.id)])
            return valid_response({"students": [
                {
                    "id": student.id,
                    "name": student.name,
                    "student_number": student.student_number,
                    "image": base64.b64encode(student.image).decode('utf-8') if student.image else None,
                    "class_name": student.class_name,
                    "parent_name": student.parent_name,
                    "parent_phone": student.parent_phone
                } for student in students
            ]
            }, 200, )
        except Exception as error:
            _logger.error(_('Error while getting students') + str(error))
            traceback.print_exc()
            return invalid_response(error, 500)
