# -*- coding: utf-8 -*-
from jose import JWTError, jwt
from datetime import datetime, timedelta
from odoo.http import request
from odoo.tools.config import config
import functools
import json


SECRET_KEY = str(config.get('SECRET_KEY'))
ALGORITHM = 'HS256'

def generate_token(data: dict, validity: int = 24 * 60):
    data_to_encode = data.copy()
    expire_time = datetime.now() + timedelta(minutes=validity)
    data_to_encode.update({"exp": expire_time})
    encoded_jwt = jwt.encode(data_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    res = {}
    if token is None:
        res['status'], res['error'] = 0, 'Token is required'
        return res
    try:
        credentials = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        res['status'], res['credentials'] = 1, credentials
    except JWTError as error:
        res['status'], res['error'] = 0, error
    return res


def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        try:
            token = request.httprequest.headers.get('Authorization')
            if not token:
                vals = request.httprequest.data.decode()
                vals = json.loads(vals)
                token = vals.get('Authorization') or "Bearer " + vals.get('token')
            if len(token.split()) != 2 and token.split()[0] != "Bearer":
                return invalid_response("Invalid Access Token: Must be like this (Bearer+space+jwt)", 401)
        except Exception:
            return invalid_response("Access Denied", 401, "Invalid Access Token")

        token = verify_token(token.split()[-1])
        if token.get('status') == 1:
            credentials = token.get('credentials')
            user = request.env['res.users'].sudo().search([
                ('id', '=', credentials.get('id')),
                ('login', '=', credentials.get('login'))])
            context = request.env.context.copy()
            context.update({'lang': user.lang or u'it_IT'})
            request.env.context = context
            request.update_env(user=user.id)
            return func(self, *args, **kwargs)
        return invalid_response("Access Denied", 401, token.get('error'))

    return wrap

def has_permission(permissions):
    def wrap(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            token = request.httprequest.headers.get('Authorization')
            token = verify_token(token.split()[-1])
            if token.get('status') == 1:
                credentials = token.get('credentials')
            
            user = request.env['res.users'].sudo().search([('id', '=', credentials.get('id'))])
            user_permissions = [permission.name for permission in user.role_ids.permission_ids]
            is_authorized = False
            for permission in permissions:
                if permission in user_permissions:
                    is_authorized = True
            if not is_authorized:
                return invalid_response("Access Denied", 403)
            return func(self, *args, **kwargs)
        return inner
    return wrap

def valid_response(data: list | dict, status, message=None, metadata=None):
    response = {"data": [], "object": None}
    if isinstance(data, list):
        response['data'] = data
    else:
        response['object'] = data
    
    if message: response['message'] = message
    if metadata: response['metadata'] = metadata
    return request.make_json_response(response, status=status)


def invalid_response(error=None, status=400, message=None):
    response = {"error": error}
    if message: response['message'] = message
    return request.make_json_response(response, status=status)


def generate_refresh_access_token(refresh_token):
    payload = verify_token(refresh_token.split()[-1])
    if payload.get('status') == 1:
        credentials = payload.get('credentials')
        data = {
            'email': credentials['email'],
            'name': credentials['name'],
            'id': credentials['id']
        }
        new_token = generate_token(data=data)
        return {'status': 1, 'token': new_token}
    else:
        return {'status': 0, 'error': payload.get('error')}
