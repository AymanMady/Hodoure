from ..helpers import notify_whatsapp
from odoo import models, fields, api
import json
import logging

_logger = logging.getLogger(__name__)

class Absence(models.Model):
    _name = 'hodoure.absence'
    _description = 'Absence'

    absent_student_ids = fields.Many2many('hodoure.student', 'absence_student_rel', 'absence_id', 'student_id', string='Absent Students', required=True)
    teacher_id = fields.Many2one('hodoure.teacher', required=True)
    date = fields.Datetime(required=True, default=fields.Datetime.now)
    class_id = fields.Many2one('hodoure.class', string='Class', required=True)
    subject_id = fields.Many2one('hodoure.subject', string='Subject', required=True)
    period_id = fields.Many2one('hodoure.period', string='Period', required=True)
    school_id = fields.Many2one('hodoure.school')

    @api.model
    def create(self, vals):
        vals['school_id'] = self.env.user.school_id.id
        return super(Absence, self).create(vals)

    @api.model
    def action_save_absence(self, vals):
        return True
    def notify_absence(self):
        """Send WhatsApp notifications for this absence"""

        success_count = 0
        failed_count = 0
        
        for student in self.absent_student_ids:
            if not student.parent_id or not student.parent_id.phone:
                _logger.warning(f"Parent or phone number not found for student {student.name}")
                continue
                
            message = f"Dear {student.parent_id.name}, Your child {student.name} has been marked absent by {self.teacher_id.name} on {self.date.strftime('%Y-%m-%d %H:%M')} during the {self.period} period."
            
            try:
                response_str = notify_whatsapp(message, student.parent_id.phone)
                
                # Parse the JSON response
                try:
                    response = json.loads(response_str)
                except json.JSONDecodeError:
                    _logger.error(f"Invalid JSON response from WhatsApp API: {response_str}")
                    response = {"sent": "false", "message": "Invalid response format"}
                
                if response.get('sent') == "true":
                    # Notification sent successfully
                    self.env['hodoure.notification'].create({
                        'absence_id': self.id,
                        'parent_id': student.parent_id.id,
                        'type': 'whatsapp',
                        'statut': 'sent',
                        'contenu': message,
                    })
                    success_count += 1
                    _logger.info(f"WhatsApp notification sent to {student.parent_id.name} for absence of {student.name}.")
                else:
                    # Failed to send
                    self.env['hodoure.notification'].create({
                        'absence_id': self.id,
                        'parent_id': student.parent_id.id,
                        'type': 'whatsapp',
                        'statut': 'failed',
                        'contenu': message,
                    })
                    failed_count += 1
                    _logger.error(f"Failed to send WhatsApp notification to {student.parent_id.name}")
                    
            except Exception as e:
                # Handle errors
                self.env['hodoure.notification'].create({
                    'absence_id': self.id,
                    'parent_id': student.parent_id.id,
                    'type': 'whatsapp',
                    'statut': 'failed',
                    'contenu': message,
                })
                failed_count += 1
                _logger.error(f"Error sending notification to {student.parent_id.name}: {str(e)}")
        
        # Return message to user
        if success_count > 0 and failed_count == 0:
            message = f"All notifications sent successfully ({success_count})"
            notification_type = 'success'
        elif success_count > 0 and failed_count > 0:
            message = f"{success_count} notifications sent, {failed_count} failed"
            notification_type = 'warning'
        else:
            message = f"All notifications failed ({failed_count})"
            notification_type = 'danger'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Notifications',
                'message': message,
                'type': notification_type,
                'sticky': False,
            }
        }

