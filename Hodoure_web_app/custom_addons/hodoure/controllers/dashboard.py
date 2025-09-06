from odoo import http
from odoo.http import request
import json

class DashboardController(http.Controller):
    
    @http.route('/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        """API endpoint pour récupérer les données du dashboard"""
        dashboard = request.env['hodoure.dashboard']
        data = dashboard.get_dashboard_data()
        return data
    
    @http.route('/dashboard', type='http', auth='user')
    def dashboard_view(self):
        """Route pour afficher le dashboard"""
        return request.render('your_module.dashboard_template')