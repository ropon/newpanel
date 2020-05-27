#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/1 16:57
# @Author  : Ropon
# @File    : mysql.py

from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse
from api.models import SysConf, Mysql
from api.utils.response import BaseResponse, api_abort
from api.utils.tools import getRandomString
from api.utils.config import per_page
from api.utils.tools import check
from api.utils.mysql import PanelMysql

mysql_bp = Blueprint("mysql_bp", __name__, url_prefix="/api/v1")
api = Api(mysql_bp)


class MysqlView(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        if request.method == "POST":
            self.parser.add_argument('mysql_user', type=str, required=True, help='Mysql用户名不能为空', location="json")
        elif request.method == "DELETE" or "PUT":
            self.parser.add_argument('nid', type=int, required=True, help='nid不能为空', location="json")
        try:
            mysql_root = SysConf.query.first().mysql_root
        except:
            mysql_root = "West.cn2020"
        self.mysqlop = PanelMysql("root", mysql_root, "mysql")

    def get(self):
        nid = request.args.get("nid", "", type=int)
        status = request.args.get("status", 1, type=int)
        page = request.args.get("page", 1, type=int)
        num = request.args.get("num", per_page, type=int)
        extra = {"status": status}
        mysql_user = request.args.get("mysql_user")
        res = BaseResponse()
        if nid:
            extra["nid"] = nid
        if mysql_user:
            extra["ftp_user"] = mysql_user
        mysqls = Mysql.search(extra, page, num)
        if not mysqls.items:
            page = mysqls.pages
            mysqls = Mysql.search(extra, page, num)
        res.pages = mysqls.pages
        if mysqls.has_prev:
            res.prev = page - 1
        if mysqls.has_next:
            res.next = page + 1
        res.data = [mysql.to_json() for mysql in mysqls.items]
        res.page = page
        res.total = mysqls.pages * num
        return res.dict

    def post(self):
        rets = self.mysqlop.check()
        if rets:
            api_abort(httpcode=400, errcode=4025, key=rets)
        self.parser.parse_args()
        orgin_data = request.json
        mysql_user = orgin_data.get("mysql_user")
        if mysql_user == "":
            return api_abort(errcode=4012)
        orgin_data["mysql_name"] = orgin_data.get("mysql_name") or mysql_user
        orgin_data["mysql_passwd"] = orgin_data.get("mysql_passwd") or getRandomString()
        orgin_data["accept"] = orgin_data.get("accept") or "localhost"
        orgin_data["note"] = orgin_data.get("note") or mysql_user
        accept = orgin_data.get("accept")
        extra = {"mysql_user": mysql_user}
        check(Mysql, extra=extra, accept=accept)
        extra = {"mysql_name": orgin_data.get("mysql_name")}
        check(Mysql, extra=extra)
        create_dict = {
            "mysql_user": mysql_user,
            "mysql_passwd": orgin_data.get("mysql_passwd"),
            "mysql_name": orgin_data.get("mysql_name"),
            "accept": accept
        }
        # 创建mysql数据库
        result = self.mysqlop.create_mysql(**create_dict)
        mysqlobj = Mysql(**orgin_data)
        mysqlobj.add()
        res = BaseResponse()
        res.errmsg = result
        res.data = mysqlobj.to_json()
        return res.dict

    def delete(self):
        self.parser.parse_args()
        nid = request.json.get("nid")
        if nid == "":
            return api_abort(errcode=4012)
        mysqlobj = Mysql.get(nid)
        if mysqlobj:
            delete_dict = {
                "mysql_user": mysqlobj.mysql_user,
                "mysql_name": mysqlobj.mysql_name,
                "accept": mysqlobj.accept
            }
            # 删除数据库
            result = self.mysqlop.delete_mysql(**delete_dict)
            Mysql.delete(nid)
            res = BaseResponse()
            res.errmsg = result
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
        mysql_obj = Mysql.get(nid)
        if mysql_obj:
            if orgin_data:
                accept = orgin_data.get("accept")
                check(Mysql, accept=accept)
                update_dict = {
                    "mysql_user": mysql_obj.mysql_user,
                    "old_passwd": mysql_obj.mysql_passwd,
                    "mysql_passwd": orgin_data.get("mysql_passwd"),
                    "mysql_name": mysql_obj.mysql_name,
                    "accept": accept,
                    "old_accept": mysql_obj.accept
                }
                # 更新数据库
                result = self.mysqlop.update_mysql(**update_dict)
                Mysql.update(nid, orgin_data)
                ftp_dict = mysql_obj.to_json()
                res = BaseResponse()
                res.data = ftp_dict
                res.errmsg = result
                return res.dict
            else:
                # 未传入修改的值
                return api_abort(errcode=4019)
        else:
            # 记录不存在
            return api_abort(errcode=4018)


api.add_resource(MysqlView, "/mysql", endpoint="mysql")
