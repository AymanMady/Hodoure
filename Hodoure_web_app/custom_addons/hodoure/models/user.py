from odoo import models, fields

class User(models.Model):
    _inherit = 'res.users'
    _description = 'User'

    teacher_id = fields.Many2one('hodoure.teacher')
    school_id = fields.Many2one('hodoure.school')
