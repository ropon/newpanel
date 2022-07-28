#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 10:19
# @Author  : Ropon
# @File    : auth.py

import time, datetime, hashlib
from flask import request
from api.models import User, Token


def verify_token():
    username = request.headers.get("username")
    otime = request.headers.get("otime", type=int)
    token = request.headers.get("accesstoken")
    if not username or not otime or not token:
        return dict(errcode=4023)
    try:
        if int(int(time.time() - otime) / 60) > 5:
            return dict(errcode=4026)
    except:
        return dict(errcode=4026)
    user_obj = User.query.filter_by(username=username).first()
    if not user_obj:
        return dict(errcode=4023)
    token_obj = Token.query.filter_by(user_id=user_obj.nid).first()
    if token_obj:
        delta = datetime.datetime.now() - token_obj.created
        state = delta < datetime.timedelta(weeks=1)
        if not state:
            # token失效 认证超时
            return dict(errcode=4024)
        obj = hashlib.md5()
        sign = (username + str(otime) + token_obj.key).encode('utf-8')
        obj.update(sign)
        if obj.hexdigest() == token:
            return dict(userinfo=token_obj.token2user, token=token)
    # 无效token 认证失败
    return dict(errcode=4023)
