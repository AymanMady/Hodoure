import base64
import json

from odoo import http, _
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request
from odoo.tools.config import config

from .common import invalid_response, valid_response, generate_token, generate_refresh_access_token, validate_token
# from ..helpers import get_domain, is_dev_env
# from ..mails.password_reset_mail import PasswordResetMail, PasswordResetMailData
# from ..services.mail.mail_service import MailService

import logging
import traceback

_logger = logging.getLogger(__name__)

SECRET_KEY = str(config.get('SECRET_KEY'))
ALGORITHM = 'HS256'

class AuthenticationApi(http.Controller):

    @http.route("/v1/databases", methods=["OPTIONS", "GET"], type="http", cors="*", auth="none", csrf=False)
    def get_databases(self):
        config['db_name'] = False
        dbs = http.db_list()
        return valid_response(dbs, 200)

    @http.route("/v1/auth/token", methods=["OPTIONS", "POST"], type="http", cors="*", auth="none", csrf=False)
    def login(self):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Basic '):
            return invalid_response("Authentication Failed", 401)

        base64_credentials = auth_header[len('Basic '):]
        credentials = base64.b64decode(base64_credentials).decode('utf-8')
        database = str(config.get('db_name'))
        email, password = credentials.split(':', 2)

        if not all([database, email, password]):
            return invalid_response("Access Denied", 401)

        try:
            user = request.env['res.users'].authenticate(database, email.lower().strip(), password, {'interactive': False})
            if not user:
                return invalid_response("Access Denied", 401)

            request.update_env(user=user)

            data = {
                'id': user,
                'login': str(request.env.user.login),
                'name': str(request.env.user.name),
                'lang': str(request.env.user.lang),
                'database': database,
            }
            token = generate_token(data=data)
            if not token:
                return invalid_response("Access Denied", 401)

            return valid_response({"access_token": token, "user": data}, 200, "Login Success")

        except (AccessError, AccessDenied) as error:
            traceback.print_exc()
            return invalid_response("Could not login. Try again!", 400)

        except Exception as error:
            traceback.print_exc()
            return invalid_response("Database Connection Failed", 401, error)

    # @http.route("/v1/auth/refresh/token", methods=["OPTIONS", "POST"], type="http", cors="*", auth="none", csrf=False)
    # def refresh_token(self):
    #     token = json.loads(request.httprequest.data.decode()).get('access_token')
    #     if not token:
    #         return invalid_response("Refresh token is missing", 400)

    #     try:
    #         new_token = generate_refresh_access_token(token)
    #         if not new_token.get('status') == 1:
    #             return invalid_response("Access Denied", 401, new_token.get('error'))
    #         return valid_response([{"access_token": new_token.get('token')}], 200, "Token Refreshed Successfully")

    #     except Exception as error:
    #         return invalid_response("Failed to refresh token", 500, str(error))

    # @http.route("/v1/auth/forgot-password", methods=["POST"], type="http", cors="*", auth="none", csrf=False)
    # def forgot_password(self):
    #     args = request.httprequest.data.decode()
    #     vals = json.loads(args)
    #     login = vals.get('email', False)
    #     if not login or not login.strip():
    #         return invalid_response("Invalid Email", 400)
    #     login = login.lower().strip()
    #     try:
    #         user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
    #         if not user:
    #             return invalid_response("User not found", 404)

    #         origin = request.httprequest.environ.get('HTTP_ORIGIN', False)
    #         host = request.httprequest.environ.get('HTTP_HOST', False)

    #         if not origin:
    #             return invalid_response("Invalid Request", 400)

    #         token = generate_token(data={'id': user.id, 'email': str(user.login)}, validity=60)
    #         scheme = request.httprequest.scheme
    #         domain = get_domain(origin, user.is_retailer)
    #         path = f"/reset-password/{token}"

    #         if is_dev_env(host):
    #             return valid_response(None, 200, f"Local env. Go to {scheme}://{domain}{path} to reset password")

    #         mail_data = PasswordResetMailData(
    #             email_title= _('Password Reset'), 
    #             email_subtitle='',
    #             reset_password_url=f"{scheme}://{domain}{path}", 
    #             base_url=host,
    #             sender_user=request.env.company.sudo().name
    #         )

    #         MailService(request.env).send_mail(
    #             model='res.users',
    #             template_name="Reset Password",
    #             record=user,
    #             email_data=PasswordResetMail(data=mail_data),
    #             cc_emails=None,
    #             send_to_queue=False
    #         )

    #         return valid_response(None, 200, "Password reset instructions sent to your email")

    #     except Exception as error:
    #         traceback.print_exc()
    #         _logger.error(error)
    #         return invalid_response("Failed to send password reset instructions", 400)

    # @validate_token
    # @http.route("/v1/auth/reset-password", methods=["OPTIONS", "POST"], type="http", cors="*", auth="none", csrf=False)
    # def reset_password(self):
    #     args = request.httprequest.data.decode()
    #     if not args:
    #         return invalid_response("Invalid Request", 400)
    #     vals = json.loads(args)
    #     password = vals.get('newPassword', False)
    #     confirm_passwd = vals.get('confirmPassword', False)

    #     if not password or not confirm_passwd:
    #         return invalid_response("Password and Confirm Password are required", 400)

    #     if password != confirm_passwd:
    #         return invalid_response("Password and Confirm Password does not match", 400)

    #     user = request.env.user
    #     if not user or not user.id:
    #         return invalid_response("User not found", 404)

    #     try:
    #         user._change_password(password)
    #         return valid_response(None, 200, "Password Reset Successfully")

    #     except Exception as error:
    #         traceback.print_exc()
    #         _logger.error(error)
    #         return invalid_response("Failed to reset password", 400)

