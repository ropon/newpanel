#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/24 14:59
# @Author  : Ropon
# @File    : config.py

import os


class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                          'panel.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    JSONIFY_MIMETYPE = "application/json;charset=utf-8"
    RESTFUL_JSON = dict(ensure_ascii=False)


class DevConfig(Config):
    DEBUG = True


class ProConfig(Config):
    pass
