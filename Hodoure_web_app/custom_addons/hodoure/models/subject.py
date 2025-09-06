from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Subject(models.Model):
    _name = 'hodoure.subject'
    _description = 'Subject'

    name = fields.Char(required=True)
    school_id = fields.Many2one('hodoure.school')

    @api.model
    def create(self, vals):
        vals['school_id'] = self.env.user.school_id.id
        return super(Subject, self).create(vals)

    def action_save_subject(self):
        self.ensure_one()
        try:
            if not self.name:
                raise ValidationError("Subject name is required.")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Subject {self.name} has been saved successfully.',
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

