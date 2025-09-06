
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Student(models.Model):
    _name = 'hodoure.student'
    _description = 'Student'

    name = fields.Char(required=True)
    name_fr = fields.Char(string="French Name")
    student_number = fields.Char(string="Student Code", required=True)
    image = fields.Binary("Image")
    class_id = fields.Many2one('hodoure.class', required=True)
    class_name = fields.Char()
    parent_id = fields.Many2one('hodoure.parent', required=True)
    parent_name = fields.Char()
    parent_phone = fields.Char()
    school_id = fields.Many2one('hodoure.school')

    @api.model
    def create(self, vals):
        vals['school_id'] = self.env.user.school_id.id
        if vals.get('parent_name') and vals.get('parent_phone'):
            parent = self.env['hodoure.parent'].search([('phone', '=', vals['parent_phone']),('school_id', '=', vals['school_id'])], limit=1)
            if not parent: 
                parent = self.env['hodoure.parent'].create({'phone': vals['parent_phone'],'name': vals['parent_name'],'school_id': vals['school_id']})
            vals['parent_id'] = parent.id

        if vals.get('class_name'):
            classe = self.env['hodoure.class'].search([('name', '=', vals['class_name']),('school_id', '=', vals['school_id'])], limit=1)
            if not classe:
                classe = self.env['hodoure.class'].create({'name': vals['class_name'],'niveau': vals['class_name'],'school_id': vals['school_id']})
            vals['class_id'] = classe.id
        return super(Student, self).create(vals)
    
    def action_save_student(self):
        self.ensure_one()
        try:
            if not self.name:
                raise ValidationError("Student name is required.")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Student {self.name} has been saved successfully.',
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
