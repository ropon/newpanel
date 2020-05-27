#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/1 16:57
# @Author  : Ropon
# @File    : ftp.py

from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse
from api.models import Ftp
from api.utils.response import BaseResponse, api_abort
from api.utils.tools import getRandomString
from api.utils.config import www_path, per_page
from api.utils.tools import check
from api.utils.ftp import PanelFtp

ftp_bp = Blueprint("ftp_bp", __name__, url_prefix="/api/v1")
api = Api(ftp_bp)


class FtpView(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        if request.method == "POST":
            self.parser.add_argument('ftp_user', type=str, required=True, help='Ftp用户名不能为空', location="json")
        elif request.method == "DELETE" or "PUT":
            self.parser.add_argument('nid', type=int, required=True, help='nid不能为空', location="json")
        self.ftpop = PanelFtp()

    def get(self):
        nid = request.args.get("nid", "", type=int)
        # status = request.args.get("status", "1", type=int)
        page = request.args.get("page", 1, type=int)
        num = request.args.get("num", per_page, type=int)
        # extra = {"status": status}
        extra = {}
        ftp_user = request.args.get("ftp_user")
        res = BaseResponse()
        if nid:
            extra["nid"] = nid
        if ftp_user:
            extra["ftp_user"] = ftp_user
        ftps = Ftp.search(extra, page, num)
        if not ftps.items:
            page = ftps.pages
            ftps = Ftp.search(extra, page, num)
        res.pages = ftps.pages
        if ftps.has_prev:
            res.prev = page - 1
        if ftps.has_next:
            res.next = page + 1
        res.data = [ftp.to_json() for ftp in ftps.items]
        res.page = page
        res.total = ftps.pages * num
        return res.dict

    def post(self):
        rets = self.ftpop.check()
        if rets:
            api_abort(httpcode=400, errcode=4025, key=rets)
        self.parser.parse_args()
        orgin_data = request.json
        ftp_user = orgin_data.get("ftp_user")
        if ftp_user == "":
            return api_abort(errcode=4012)
        orgin_data["ftp_passwd"] = orgin_data.get("ftp_passwd") or getRandomString()
        orgin_data["ftp_path"] = orgin_data.get("ftp_path") or f'{www_path}/{ftp_user}'
        orgin_data["note"] = orgin_data.get("note") or ftp_user
        parms = {"ftp_user": ftp_user}
        check(Ftp, extra=parms, obj_path=orgin_data["ftp_path"])
        create_dict = {
            "ftp_user": ftp_user,
            "ftp_passwd": orgin_data.get("ftp_passwd"),
            "ftp_path": orgin_data.get("ftp_path")
        }
        # 创建FTP站点
        self.ftpop.create_ftp(**create_dict)
        ftpobj = Ftp(**orgin_data)
        ftpobj.add()
        res = BaseResponse()
        res.data = ftpobj.to_json()
        return res.dict

    def delete(self):
        self.parser.parse_args()
        nid = request.json.get("nid")
        if nid == "":
            return api_abort(errcode=4012)
        ftpobj = Ftp.get(nid)
        if ftpobj:
            self.ftpop.delete_ftp(ftp_user=ftpobj.ftp_user, ftp_path=ftpobj.ftp_path)
            Ftp.delete(nid)
            res = BaseResponse()
            res.dict.pop("data")
            return res.dict
        else:
            return api_abort(errcode=4018)

    def put(self):
        self.parser.parse_args()
        orgin_data = request.json
        nid = orgin_data.pop("nid")
        if nid == "":
            return api_abort(errcode=4012)
        # 站点名、路径不支持修改
        orgin_data.pop("ftp_user", "")
        orgin_data.pop("ftp_path", "")
        ftp_obj = Ftp.get(nid)
        if ftp_obj:
            if orgin_data:
                self.ftpop.update_ftp(status=orgin_data.get("status"), ftp_user=ftp_obj.ftp_user,
                                      ftp_passwd=orgin_data.get("ftp_passwd"))
                Ftp.update(nid, orgin_data)
                ftp_dict = ftp_obj.to_json()
                res = BaseResponse()
                res.data = ftp_dict
                return res.dict
            else:
                # 未传入修改的值
                return api_abort(errcode=4019)
        else:
            # 记录不存在
            return api_abort(errcode=4018)


api.add_resource(FtpView, "/ftp", endpoint="ftp")
