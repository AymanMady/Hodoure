from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Period(models.Model):
    _name = 'hodoure.period'
    _description = 'Period'

    name = fields.Char(required=True)
    school_id = fields.Many2one('hodoure.school')

    @api.model
    def create(self, vals):
        vals['school_id'] = self.env.user.school_id.id
        return super(Period, self).create(vals)

    def action_save_period(self):
        self.ensure_one()
        try:
            if not self.name:
                raise ValidationError("Period name is required.")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Period {self.name} has been saved successfully.',
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
