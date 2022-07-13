#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/18 11:19
# @Author  : Ropon
# @File    : soft.py

import os
from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse
from api.models import Soft
from api.utils.response import BaseResponse, api_abort
from api.utils.config import per_page
from api.utils.tools import execShell
# from flask_socketio import send, emit
# from api import socketio

soft_bp = Blueprint("soft_bp", __name__, url_prefix="/api/v1")
api = Api(soft_bp)


class SoftView(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        if request.method == "POST":
            self.parser.add_argument('soft_name', type=str, required=True, help='软件名不能为空', location="json")
            self.parser.add_argument('soft_ver', type=str, required=True, help='软件版本不能为空', location="json")
        elif request.method == "DELETE" or "PUT":
            self.parser.add_argument('nid', type=int, required=True, help='nid不能为空', location="json")
        self.shellpath = "/home/panel/newpanel/shell"

    def get(self):
        nid = request.args.get("nid", "", type=int)
        page = request.args.get("page", 1, type=int)
        num = request.args.get("num", per_page, type=int)
        extra = {}
        if nid:
            extra["nid"] = nid
        soft_name = request.args.get("soft_name")
        res = BaseResponse()
        if soft_name:
            extra["soft_name"] = soft_name
        softs = Soft.search(extra, page, num)
        if not softs.items:
            page = softs.pages
            softs = Soft.search(extra, page, num)
        res.pages = softs.pages
        if softs.has_prev:
            res.prev = page - 1
        if softs.has_next:
            res.next = page + 1
        res.page = page
        res.total = softs.pages * num
        res.data = [soft.to_json() for soft in softs.items]
        return res.dict

    def post(self):
        self.parser.parse_args()
        orgin_data = request.json
        soft_name = orgin_data.get("soft_name")
        soft_ver = orgin_data.get("soft_ver")
        if soft_name == "" or soft_ver == "":
            return api_abort(errcode=4012)
        orgin_data["soft_desc"] = orgin_data.get("soft_desc") or soft_name
        softobj = Soft(**orgin_data)
        softobj.add()
        res = BaseResponse()
        res.data = softobj.to_json()
        return res.dict

    def delete(self):
        self.parser.parse_args()
        nid = request.json.get("nid")
        if nid == "":
            return api_abort(errcode=4012)
        soft_obj = Soft.get(nid)
        if soft_obj:
            Soft.delete(nid)
            res = BaseResponse()
            res.dict.pop("data")
            return res.dict
        else:
            return api_abort(errcode=4018)

    def put(self):
        self.parser.parse_args()
        orgin_data = request.json
        nid = orgin_data.pop("nid")
        installtype = orgin_data.get("installtype")
        soft_name = orgin_data.get("soft_name")
        soft_ver = orgin_data.get("soft_ver")
        if nid == "":
            return api_abort(errcode=4012)
        soft_obj = Soft.get(nid)
        if soft_obj:
            if orgin_data:
                softobj = Soft.query.filter_by(**{'soft_name': soft_name, 'is_install': 1}).first()
                if softobj:
                    api_abort(httpcode=400, errcode=4025, key=f"已安装{softobj.soft_name},若要安装新版请先卸载")
                softobj2 = Soft.query.filter_by(**{'is_install': 2}).first()
                if softobj2:
                    api_abort(httpcode=400, errcode=4025, key=f"正在安装{softobj2.soft_name},请稍后重试")
                if installtype == "rpm":
                    api_abort(httpcode=400, errcode=4025, key=f"暂时不支持极速安装")
                    # res = 0
                    Soft.update(nid, {"is_install": 2})
                    res = os.system(f"/bin/bash {self.shellpath}/{soft_name}_rpm.sh {soft_ver}")
                elif installtype == "bash":
                    Soft.update(nid, {"is_install": 2})
                    res = os.system(f"/bin/bash {self.shellpath}/{soft_name}.sh {soft_ver}")
                    # res = execShell(f"bash {self.shellpath}/{soft_name}.sh {soft_ver}")
                    if res == 1:
                        Soft.update(nid, {"is_install": 0})
                        api_abort(httpcode=400, errcode=4025, key=f"{soft_name}安装失败")
                Soft.update(nid, {"is_install": 1})
                soft_dict = soft_obj.to_json()
                res = BaseResponse()
                res.data = soft_dict
                res.errmsg = f"正在安装{soft_name}..."
                return res.dict
            else:
                # 未传入修改的值
                return api_abort(errcode=4019)
        else:
            # 记录不存在
            return api_abort(errcode=4018)

    # @socketio.on('message')
    # def handle_message(self, message):
    #     print(message)
    #     send(message)
    #
    # @socketio.on('connect', namespace='/chat')
    # def test_connect(self):
    #     emit('my response', {'data': 'Connected'})
    #
    # @socketio.on('disconnect', namespace='/chat')
    # def test_disconnect(self):
    #     print('Client disconnected')


api.add_resource(SoftView, "/soft", endpoint="soft")
