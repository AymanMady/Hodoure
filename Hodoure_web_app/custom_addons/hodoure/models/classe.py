from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Classe(models.Model):
    _name = 'hodoure.class'
    _description = 'Class'

    name = fields.Char(required=True)
    niveau = fields.Char()
    school_id = fields.Many2one('hodoure.school')

    @api.model
    def create(self, vals):
        vals['school_id'] = self.env.user.school_id.id
        return super(Classe, self).create(vals)

    def action_save_class(self):
        self.ensure_one()
        try:
            if not self.name:
                raise ValidationError("Class name is required.")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Class {self.name} has been saved successfully.',
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
