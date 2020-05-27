#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/1 16:57
# @Author  : Ropon
# @File    : site.py

import json
from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse
from api.models import Site, SiteInfo
from api.utils.response import BaseResponse, api_abort
from api.utils.config import www_path, logs_path, per_page, default_index, php_ver, extra_kwargs_dict
from api.utils.tools import check
from api.utils.site import PanelSite

site_bp = Blueprint("site_bp", __name__, url_prefix="/api/v1")
api = Api(site_bp, default_mediatype="application/json;charset=utf-8")


class SiteView(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        if request.method == "POST":
            self.parser.add_argument('site_name', type=str, required=True, help='站点名不能为空', location="json", trim=True)
            self.parser.add_argument('bind_domain', type=str, required=True, help='绑定域名不能为空', location="json",
                                     trim=True)
        elif request.method == "DELETE" or "PUT":
            self.parser.add_argument('nid', type=int, required=True, help='nid不能为空', location="json", trim=True)
        self.siteop = PanelSite()

    def get(self):
        nid = request.args.get("nid", "", type=int)
        status = request.args.get("status", 1, type=int)
        page = request.args.get("page", 1, type=int)
        num = request.args.get("num", per_page, type=int)
        extra = {"status": status}
        site_name = request.args.get("site_name")
        bind_domain = request.args.get("bind_domain")
        res = BaseResponse()
        if nid:
            extra["nid"] = nid
        if site_name:
            extra["site_name"] = site_name
        sites = Site.search(extra, bind_domain, page, num)
        if not sites.items:
            page = sites.pages
            sites = Site.search(extra, bind_domain, page, num)
        res.pages = sites.pages
        if sites.has_prev:
            res.prev = page - 1
        if sites.has_next:
            res.next = page + 1
        site_list = []
        for site in sites.items:
            site_dict = site.to_json()
            site_info = SiteInfo.sget(site.nid)
            if site_info:
                site_dict["site_info"] = site_info.to_json()
            site_list.append(site_dict)
        res.page = page
        res.total = sites.pages * num
        res.data = site_list
        return res.dict

    def post(self):
        rets = self.siteop.check()
        if rets:
            api_abort(httpcode=400, errcode=4025, key=rets)
        self.parser.parse_args()
        orgin_data = request.json
        site_name = orgin_data.get("site_name", "")
        bind_domain = orgin_data.get("bind_domain", "")
        if site_name == "" or bind_domain == "":
            api_abort(errcode=4012)
        orgin_data["root_path"] = orgin_data.get("root_path") or f'{www_path}/{site_name}'
        orgin_data["note"] = orgin_data.get("note") or site_name
        # 检查域名、路径合法性及站点、域名重复性
        parms = {"site_name": site_name}
        check(Site, bind_domain, parms, orgin_data.get("root_path"))
        orgin_data.pop("ftpinfo")
        orgin_data.pop("mysqlinfo")
        # orgin_data.pop("sslinfo")
        siteinfo_orgin_data = orgin_data.pop("site_info", {})
        if siteinfo_orgin_data.get('is_log'):
            siteinfo_orgin_data["log_path"] = f'{logs_path}/{site_name}'
        else:
            siteinfo_orgin_data["log_path"] = ""
        # 规范 port is_ssl 值
        if siteinfo_orgin_data.get("port") == 80:
            siteinfo_orgin_data["is_ssl"] = False
        elif siteinfo_orgin_data.get("port") == 443:
            siteinfo_orgin_data["is_ssl"] = True
        if siteinfo_orgin_data.get("is_ssl") == False:
            siteinfo_orgin_data["port"] = 80
        elif siteinfo_orgin_data.get("is_ssl") == True:
            siteinfo_orgin_data["port"] = 443

        extra_kwargs = siteinfo_orgin_data.pop("extra_kwargs", {}) or extra_kwargs_dict
        domain_301 = siteinfo_orgin_data.get("domain_301")
        if extra_kwargs.get('set_301') and domain_301 == "":
            api_abort(httpcode=400, errcode=4025, key="开启301,跳转域名不能为空")
        check(obj_domain=domain_301)
        siteinfo_orgin_data["extra_kwargs"] = json.dumps(extra_kwargs)
        phpver = siteinfo_orgin_data.get("php_ver") or php_ver
        create_dict = {
            "site_name": site_name,
            "bind_domain": bind_domain.replace(",", " "),
            "root_path": orgin_data.get("root_path"),
            "is_ssl": siteinfo_orgin_data.get("is_ssl") or False,
            "is_log": siteinfo_orgin_data.get('is_log') or False,
            "log_path": siteinfo_orgin_data.get("log_path"),
            "domain_301": siteinfo_orgin_data.get("domain_301") or "",
            "default_index": siteinfo_orgin_data.get("default_index") or default_index,
            "php_ver": phpver.replace(".", ""),
            "extra_kwargs": extra_kwargs
        }
        # 创建站点
        res = self.siteop.create_site(**create_dict)
        if res:
            api_abort(httpcode=400, errcode=4025, key=res)
        siteobj = Site(**orgin_data)
        siteobj.add()
        site_dict = siteobj.to_json()
        siteinfo_orgin_data["site_id"] = siteobj.nid
        siteinfoobj = SiteInfo(**siteinfo_orgin_data)
        siteinfoobj.add()
        site_info = SiteInfo.sget(siteobj.nid)
        if site_info:
            site_dict["site_info"] = site_info.to_json()
        res = BaseResponse()
        res.data = site_dict
        return res.dict

    def delete(self):
        self.parser.parse_args()
        nid = request.json.get("nid")
        print(nid)
        if nid == "":
            return api_abort(errcode=4012)
        siteobj = Site.get(nid)
        siteinfoobj = SiteInfo.sget(nid)
        if siteobj:
            self.siteop.delete_site(site_name=siteobj.site_name, root_path=siteobj.root_path, is_ssl=siteinfoobj.is_ssl,
                                    log_path=siteinfoobj.log_path)
            if siteinfoobj:
                SiteInfo.sdelete(nid)
            Site.delete(nid)
            res = BaseResponse()
            res.dict.pop("data")
            return res.dict
        else:
            return api_abort(errcode=4018)

    def put(self):
        self.parser.parse_args()
        fields = {"nid", "site_name", "bind_domain", "root_path", "site_info", "note"}
        orgin_data = {}
        if fields.issubset(set(request.json.keys())):
            for key in fields:
                orgin_data[key] = request.json.get(key)
        orgin_data = request.json
        nid = orgin_data.pop("nid")
        if nid == "":
            return api_abort(errcode=4012)
        bind_domain = orgin_data.get("bind_domain")
        # 站点名、路径不支持修改
        orgin_data.pop("site_name", "")
        orgin_data.pop("root_path", "")
        site_obj = Site.get(nid)
        if site_obj:
            check(Site, obj_domain=bind_domain, site_name=site_obj.site_name)
            bind_domain = bind_domain or site_obj.bind_domain
            siteinfo_orgin_data = orgin_data.pop("site_info", {})
            if siteinfo_orgin_data.get('is_log'):
                siteinfo_orgin_data["log_path"] = f'{logs_path}/{site_obj.site_name}'
            else:
                siteinfo_orgin_data["log_path"] = ""
            if siteinfo_orgin_data:
                extra_kwargs = siteinfo_orgin_data.pop("extra_kwargs", {})
                if extra_kwargs:
                    siteinfo_orgin_data["extra_kwargs"] = json.dumps(extra_kwargs)
            if orgin_data:
                site_info = SiteInfo.sget(nid)
                php_ver = siteinfo_orgin_data.get('php_ver') or site_info.php_ver
                domain_301 = siteinfo_orgin_data.get("domain_301")
                if extra_kwargs.get('set_301') and domain_301 == "":
                    api_abort(httpcode=400, errcode=4025, key="开启301,跳转域名不能为空")
                check(obj_domain=domain_301)
                create_dict = {
                    "site_name": site_obj.site_name,
                    "bind_domain": bind_domain.replace(",", " "),
                    "root_path": site_obj.root_path,
                    "is_ssl": siteinfo_orgin_data.get('is_ssl'),
                    "is_log": siteinfo_orgin_data.get('is_log'),
                    "log_path": siteinfo_orgin_data.get('log_path'),
                    "domain_301": domain_301,
                    "default_index": site_info.default_index,
                    "php_ver": php_ver.replace(".", ""),
                    "extra_kwargs": extra_kwargs
                }
                # 更新站点调用 创建站点
                res = self.siteop.create_site(**create_dict)
                if res:
                    api_abort(httpcode=400, errcode=4025, key=res)
                SiteInfo.supdate(nid, siteinfo_orgin_data)
                Site.update(nid, orgin_data)
                site_dict = site_obj.to_json()
                if site_info:
                    site_dict["site_info"] = site_info.to_json()
                res = BaseResponse()
                res.data = site_dict
                return res.dict
            else:
                # 未传入修改的值
                return api_abort(errcode=4019)
        else:
            # 记录不存在
            return api_abort(errcode=4018)


api.add_resource(SiteView, "/site")
