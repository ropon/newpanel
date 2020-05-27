#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/27 16:12
# @Author  : Ropon
# @File    : config.py

from api.models import SysConf

# 获取网站根目录 日志根目录
try:
    www_path = SysConf.query.first().www_path
except:
    www_path = "/home/wwwroot"
try:
    logs_path = SysConf.query.first().logs_path
except:
    logs_path = "/home/weblogs"

# 每页显示记录数
per_page = 5

# 白名单
url_prefix = "/"
URL_LIST = [url_prefix, f"{url_prefix}site", f"{url_prefix}ftp", f"{url_prefix}mysql", f"{url_prefix}soft",
            f"{url_prefix}login", f"{url_prefix}file"]
WHITE_URL_LIST = URL_LIST.copy()
WHITE_URL_LIST[0] = f"^{url_prefix}$"
WHITE_URL_LIST.append("/static/.*")
WHITE_URL_LIST.append("/api/v1/login")

# 登录尝试次数 锁定时间
lockmin = 5
trytimes = 3

# 默认文档
default_index = "index.php index.html index.htm default.php default.htm default.html"
php_ver = "php7.0"
extra_kwargs_dict = {"rewrite": "", "set_301": False, "set_404": False, "deny_ua": True, "deny_referer": True,
                     "safe": True,
                     "cache": True}
