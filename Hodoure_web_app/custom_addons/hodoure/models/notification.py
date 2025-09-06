from odoo import models, fields, api

class Notification(models.Model):
    _name = 'hodoure.notification'
    _description = 'Notification'

    absence_id = fields.Many2one('hodoure.absence')
    parent_id = fields.Many2one('hodoure.parent')
    date_envoi = fields.Datetime(default=fields.Datetime.now)
    type = fields.Selection([('sms', 'SMS'), ('email', 'Email'), ('whatsapp', 'WhatsApp')])
    statut = fields.Selection([('sent', 'Sent'), ('failed', 'Failed'), ('pending', 'Pending')], default='pending')
    contenu = fields.Text()
    school_id = fields.Many2one('hodoure.school')

    @api.model
    def create(self, vals):
        vals['school_id'] = self.env.user.school_id.id
        return super(Notification, self).create(vals)

    @api.model
    def action_save_notification(self, vals):
        return True