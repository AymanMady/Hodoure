from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import random

_logger = logging.getLogger(__name__)

class Teacher(models.Model):
    _name = 'hodoure.teacher'
    _description = 'Teacher'

    name = fields.Char(required=True)
    phone = fields.Char(required=True)
    password = fields.Char(string='Password')
    school_id = fields.Many2one('hodoure.school')
    class_ids = fields.Many2many('hodoure.class', string='Classes')

    @api.model
    def create(self, vals):
        # Check if phone is provided
        if not vals.get('phone'):
            raise ValidationError("Phone is required to create a teacher.")
        
        # Check if a user with this phone already exists
        existing_user = self.env['res.users'].search([('login', '=', vals['phone'])], limit=1)
        if existing_user:
            raise ValidationError(f"A user with phone {vals['phone']} already exists.")
        
        vals['school_id'] = self.env.user.school_id.id
        
        password = ''.join(random.choice('0123456789') for i in range(6))
        vals['password'] = password
        # Create the teacher record first
        teacher = super(Teacher, self).create(vals)

        # Create the user
        user_vals = {
            'name': teacher.name,
            'login': teacher.phone,
            'password': teacher.password,
            'email': '',
            'active': True,
            'teacher_id': teacher.id,
            'school_id': teacher.school_id.id if teacher.school_id else False,
            'action_id': self.env.ref('hodoure.hodoure_student_menu').id,
        }
        

        self.env['res.users'].create(user_vals)
        
        
        return teacher

    def write(self, vals):
        if 'phone' in vals:
            # Check if a user with this phone already exists (excluding current teacher)
            existing_user = self.env['res.users'].search([
                ('login', '=', vals['phone']),
                ('teacher_id', '!=', self.id)
            ], limit=1)
            if existing_user:
                raise ValidationError(f"A user with phone {vals['phone']} already exists.")

            # Update related user login if exists
            user = self.env['res.users'].search([('teacher_id', '=', self.id)], limit=1)
            if user:
                user.login = vals['phone']

        return super(Teacher, self).write(vals)


    def unlink(self):
        for teacher in self:
            # Check if the teacher is assigned to any classes
            if teacher.class_ids:
                raise ValidationError(
                    f"Teacher {teacher.name} cannot be deleted because they are assigned to one or more classes."
                )
            
            # Delete the related user if exists
            user = self.env['res.users'].search([('teacher_id', '=', teacher.id)], limit=1)
            if user:
                user.unlink()
        
        return super(Teacher, self).unlink()

    def action_save_teacher(self):
        self.ensure_one()
        try:
            if not self.name:
                raise ValidationError("Teacher name is required.")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Teacher {self.name} has been saved successfully.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Error during save: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

