from odoo import models, fields, api

class School(models.Model):
    _name = 'hodoure.school'
    _description = 'School'

    name = fields.Char(required=True)
    telephone = fields.Char()

    @api.model
    def action_save_school(self, vals):
        return True