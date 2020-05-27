#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/27 14:20
# @Author  : Ropon
# @File    : tools.py
import random, string, re, subprocess, shlex
from api.utils.response import api_abort
from api.utils.config import www_path


def check(models=None, obj_domain=None, extra=None, obj_path=None, site_name=None, accept=None):
    if obj_domain:
        if type(obj_domain) == str:
            domains = obj_domain.split(',')
        else:
            domains = []
        # 检查域名是否合法、重复
        reg = "^((xn--)?[A-Za-z0-9*]{1,100}\.){1,8}((xn--)?[A-Za-z0-9]){1,24}$"
        for domain in domains:
            if not re.match(reg, domain):
                return api_abort(httpcode=400, errcode=4014, key=domain)
            if models:
                site = models.query.filter(models.bind_domain.contains(domain)).first()
                if site and site_name is None:
                    return api_abort(httpcode=400, errcode=4016, key=domain)

    if extra:
        obj_name = extra.get("site_name") or extra.get("ftp_user") or extra.get("mysql_user") or extra.get(
            "mysql_name")
        reg = "^([A-Za-z0-9]{3,10})$"
        if not re.match(reg, obj_name):
            return api_abort(httpcode=400, errcode=4013, key=obj_name)
        # 检查站点名重复性
        obj_obj = models.query.filter_by(**extra).first()
        if obj_obj:
            return api_abort(httpcode=400, errcode=4017, key=obj_name)

    if obj_path:
        # 检查路径是否合法
        reg = "^%s\/([A-Za-z0-9]{1,20})(\/[A-Za-z0-9]{1,100}){0,10}$" % www_path.replace("/", "\/")
        if not re.match(reg, obj_path):
            return api_abort(httpcode=422, errcode=4015, key=obj_path)

    if accept:
        reg = "^(((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?))?(localhost)?(%)?$"
        if not re.match(reg, accept):
            return api_abort(httpcode=422, errcode=4027, key=accept)


def getRandomString(slen=8):
    return "".join(random.sample(string.ascii_letters + string.digits, slen))


def execShell(cmdstring):
    p = subprocess.Popen(cmdstring, shell=True, bufsize=4096, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = ""
    while True:
        line = p.stdout.readline().rstrip().decode('utf8')
        print(line)
        result = result + line
        if not line:
            break
    return result
