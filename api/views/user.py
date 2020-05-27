#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/29 15:46
# @Author  : Ropon
# @File    : user.py

from flask import Blueprint, request
from flask_restful import Api, Resource
from api.models import User
from api.utils.response import BaseResponse, api_abort

user_bp = Blueprint("user_bp", __name__, url_prefix="/api/v1")
api = Api(user_bp)


class UserView(Resource):

    def post(self):
        username = request.headers.get("username")
        oldpasswd = request.json.get("oldpasswd")
        newpasswd = request.json.get("newpasswd")
        print(username, oldpasswd, newpasswd)
        if username == "" or oldpasswd == "" or newpasswd == "":
            api_abort(errcode=4012)
        user_obj = User.query.filter_by(username=username).first()
        if not user_obj.check_password(user_obj.password, oldpasswd):
            api_abort(httpcode=400, errcode=4025, key="原密码不正确")
        User.update(user_obj.nid, {'password': User.set_password(newpasswd)})
        res = BaseResponse()
        res.errmsg = "密码修改成功"
        return res.dict


api.add_resource(UserView, "/user", endpoint="user")
