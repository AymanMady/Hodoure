from odoo import models, fields, api
from odoo.exceptions import AccessError

class hodoureDashboard(models.TransientModel):
    _name = 'hodoure.dashboard'
    _description = 'Dashboard Statistics'

    # Champs pour les statistiques
    student_count = fields.Integer(string='Number of Students', compute='_compute_statistics')
    teacher_count = fields.Integer(string='Number of Teachers', compute='_compute_statistics') 
    message_count = fields.Integer(string='Number of Messages', compute='_compute_statistics')

    @api.depends()
    def _compute_statistics(self):
        for record in self:
            # Compter les étudiants
            record.student_count = self.env['hodoure.student'].search_count([])
            
            # Compter les professeurs (adapter selon votre modèle)
            record.teacher_count = self.env['hodoure.teacher'].search_count([])
            
            # Compter les messages (adapter selon votre modèle)
            record.message_count = 30

    @api.model
    def get_dashboard_data(self):
        """Retourne les données pour le dashboard"""
        return {
            'students': self.env['hodoure.student'].search_count([]),
            'teachers': self.env['hodoure.teacher'].search_count([]),
            'messages': 30,
            'chart_data': self._get_chart_data()
        }

    def _get_chart_data(self):
        """Prépare les données pour les graphiques"""
        # Exemple: statistiques par classe
        classes = self.env['hodoure.class'].search([])
        chart_data = []
        
        for cls in classes:
            student_count = self.env['hodoure.student'].search_count([('class_id', '=', cls.id)])
            chart_data.append({
                'name': cls.name,
                'count': student_count
            })
        
        return chart_data