#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 13:42
# @Author  : Ropon
# @File    : login.py

import datetime
from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse
from api.utils.response import BaseResponse
from api.models import User, Token
from api.utils.tools import getRandomString
from api.utils.config import lockmin, trytimes

login_bp = Blueprint("login_bp", __name__, url_prefix="/api/v1")
api = Api(login_bp)


class LoginView(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument('username', type=str, required=True, help='用户名不能为空', location="json")
        self.parser.add_argument('password', type=str, required=True, help='密码不能为空', location="json")

    def post(self):
        self.parser.parse_args()
        username = request.json.get("username")
        password = request.json.get("password")
        user_obj = User.query.filter_by(username=username).first()
        res = BaseResponse()
        def auth():
            if user_obj.check_password(user_obj.password, password):
                token_dict = {"key": getRandomString(32), "user_id": user_obj.nid}
                # token 时效性一周
                if Token.uget(user_obj.nid):
                    Token.uupdate(user_obj.nid, token_dict)
                else:
                    token_obj = Token(**token_dict)
                    token_obj.add()
                # 登录成功初始化状态 1 错误次数 0
                User.update(user_obj.nid, {"status": 1, "errtimes": 0})
                res.data =  {"username": username, "token": token_dict.get("key")}
                return res.dict
            # 错误次数达到3次 锁定账号
            elif user_obj.errtimes == trytimes:
                User.update(user_obj.nid, {"status": 0, "locktime": newtime})
                return dict(errcode=4022, errmsg="错误次数过多，账号已锁定，请%s分钟后重试" % lockmin)
            else:
                # 错误次数+1
                User.updateplus(user_obj.nid)
                if user_obj.errtimes == trytimes:
                    User.update(user_obj.nid, {"status": 0, "locktime": newtime})
                    return dict(errcode=4022, errmsg="错误次数过多，账号已锁定，请%s分钟后重试" % lockmin)
                else:
                    return dict(errcode=4021,
                                errmsg="密码错误，还可尝试%s次，错误3次账号将锁定5分钟" % (trytimes - user_obj.errtimes))

        if user_obj is None:
            return dict(errcode=4020, errmsg="用户名不存在")
        else:
            newtime = datetime.datetime.now()
            delta = newtime - user_obj.locktime
            ctime = int(delta.total_seconds() / 60)
            if user_obj.status:
                return auth()
            else:
                if ctime < lockmin:
                    return dict(errcode=4022, errmsg="错误次数过多，账号已锁定，请%s分钟后重试" % (lockmin - ctime))
                else:
                    User.update(user_obj.nid, {"status": 1, "errtimes": 0})
                    return auth()


api.add_resource(LoginView, "/login")
