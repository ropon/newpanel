#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/29 15:46
# @Author  : Ropon
# @File    : ssl.py

from flask import Blueprint, request
from flask_restful import Api, Resource
from api.utils.response import BaseResponse, api_abort
from api.utils.tools import execShell

ssl_bp = Blueprint("ssl_bp", __name__, url_prefix="/api/v1")
api = Api(ssl_bp)


class SslView(Resource):

    def save(self, filename, content, mode="w"):
        try:
            fp = open(filename, mode)
            fp.write(content)
            fp.close()
            return True
        except:
            return False

    def post(self):
        crt = request.form.get('crt')
        key = request.form.get('key')
        site_name = request.form.get('site_name')
        bind_domain = request.form.get('bind_domain')
        if site_name == "" or bind_domain == "" or crt == "" or key == "":
            api_abort(httpcode=400, errcode=4025, key="站点名或绑定域名或证书或秘钥内容不能为空")
        crttmppath = f"/tmp/{site_name}.crt"
        keytmppath = f"/tmp/{site_name}.key"
        self.save(crttmppath, crt)
        self.save(keytmppath, key)
        from OpenSSL import crypto
        try:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, open(crttmppath).read())
            subject = cert.get_subject()
            ssl_domain = subject.CN
        except:
            api_abort(httpcode=400, errcode=4025, key="证书文件错误")
            execShell(f"rm -rf {crttmppath}")
            execShell(f"rm -rf {keytmppath}")
        ssl_domain_flag = set(bind_domain.split(',')) & set([ssl_domain, ])
        if not ssl_domain_flag:
            api_abort(httpcode=400, errcode=4025, key=f"证书不匹配,此证书文件是{ssl_domain}")
            execShell(f"rm -rf {crttmppath}")
            execShell(f"rm -rf {keytmppath}")
        execShell(f"mv {crttmppath} /home/panel/ssl/{site_name}.crt")
        execShell(f"mv {keytmppath} /home/panel/ssl/{site_name}.key")
        res = BaseResponse()
        return res.dict


api.add_resource(SslView, "/ssl", endpoint="ssl")
