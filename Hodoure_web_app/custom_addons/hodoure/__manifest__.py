{
    'name': 'hodoure',
    'version': '1.0',
    'summary': 'School Management System - Notifications',
    'description': """
        This module allows sending SMS and Whatsapp notifications for different events in the system.
        It can be used to notify users about important updates, reminders, or alerts.
    """,
    'author': 'Bechir Mady',
    'website': 'https://yourwebsite.com',
    'depends': ['base'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/student_views.xml',
        'views/teacher_views.xml',
        'views/school_views.xml',
        'views/class_views.xml',
        'views/notification_views.xml',
        'views/parent_views.xml',
        'views/absence_views.xml',
        'views/subject_views.xml',
        'views/period_views.xml',
        # 'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # 'hodoure/static/src/css/dashboard.css',
            # 'hodoure/static/src/js/dashboard.js',
            # 'hodoure/static/src/xml/dashboard_template.xml',
        ],
    },
}