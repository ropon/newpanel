#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/1 15:23
# @Author  : Ropon
# @File    : __init__.py

import re
import flask_restful
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
# from flask_socketio import SocketIO
from api.utils.response import api_abort

db = SQLAlchemy()
async_mode = None
# socketio = SocketIO()

from api.utils.config import WHITE_URL_LIST, URL_LIST
from .views.login import login_bp
from .views.site import site_bp
from .views.ftp import ftp_bp
from .views.mysql import mysql_bp
from .views.home import home_bp
from .views.soft import soft_bp
from .views.ssl import ssl_bp
from .views.user import user_bp
# from .views.socket import socket_bp
from .views.file import file_bp


def create_app():
    app = Flask(__name__)
    # debug
    # app.config.from_object("api.config.DevConfig")
    app.config.from_object("api.config.ProConfig")

    @app.before_request
    def before_request():
        # 白名单
        for white_url in WHITE_URL_LIST:
            if re.match(white_url, request.path):
                return None
        from api.utils.auth import verify_token
        auth = verify_token()
        if auth.get("userinfo") and auth.get("token"):
            return None
        else:
            return api_abort(httpcode=200, **auth)

    @app.after_request
    def after_request(response):
        # 允许跨域
        response.headers.add('Access-Control-Allow-Origin', '*')
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'POST, DELETE, PUT, GET'
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers
        return response

    def home():
        return render_template("index.html")

    for url in URL_LIST:
        app.add_url_rule(url, "home", home)

    db.init_app(app)
    # socketio.init_app(app=app, async_mode=async_mode)
    flask_restful.abort = api_abort

    app.register_blueprint(login_bp)
    app.register_blueprint(site_bp)
    app.register_blueprint(ftp_bp)
    app.register_blueprint(mysql_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(soft_bp)
    app.register_blueprint(ssl_bp)
    app.register_blueprint(user_bp)
    # app.register_blueprint(socket_bp)
    app.register_blueprint(file_bp)

    return app
