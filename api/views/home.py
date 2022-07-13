#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/11 10:20
# @Author  : Ropon
# @File    : home.py

import os, psutil, time
from flask import Blueprint, request
from flask_restful import Api, Resource
from api.utils.response import BaseResponse
from api.utils.tools import execShell

home_bp = Blueprint("home_bp", __name__, url_prefix="/api/v1")
api = Api(home_bp)


class HomeView(Resource):
    def get(self):
        info = request.args.get("info")
        data = {}
        if info == "loadavg":
            loadavg = os.getloadavg()
            data['one'] = round(loadavg[0], 2)
            data['five'] = round(loadavg[1], 2)
            data['fifteen'] = round(loadavg[2], 2)
        elif info == "sysinfo":
            data['cputype'] = execShell("cat /proc/cpuinfo |grep 'model name'").split(':')[-1].strip()
            data['cpunum'] = psutil.cpu_count()
            meminfo = psutil.virtual_memory()
            data['memtotal'] = f"{int(meminfo.total / 1024 / 1024)} MB"
            data['memfree'] = f"{int(meminfo.free / 1024 / 1024)} MB"
            data['mempercent'] = f"{meminfo.percent}%"
        elif info == "diskinfo":
            dainfo = psutil.disk_usage('/')
            data['datotal'] = f"{int(dainfo.total / 1024 / 1024 / 1024)}G"
            data['dafree'] = f"{int(dainfo.free / 1024 / 1024 / 1024)}G"
            data['dapercent'] = f"{dainfo.percent}%"
        elif info == "netinfo":
            def get_key():
                key_info = psutil.net_io_counters(pernic=True).keys()  # 获取网卡名称
                recv = {}
                sent = {}
                for key in key_info:
                    recv.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_recv)  # 各网卡接收的字节数
                    sent.setdefault(key, psutil.net_io_counters(pernic=True).get(key).bytes_sent)  # 各网卡发送的字节数
                return key_info, recv, sent

            key_info, old_recv, old_sent = get_key()
            time.sleep(1)
            key_info, now_recv, now_sent = get_key()
            net_in = {}
            net_out = {}
            for key in key_info:
                net_in.setdefault(key,
                                  f"{format((now_recv.get(key) - old_recv.get(key)) / 1024, '0.2f')} Kb/s")  # 每秒接收速率
                net_out.setdefault(key,
                                   f"{format((now_sent.get(key) - old_sent.get(key)) / 1024, '0.2f')} Kb/s")  # 每秒发送速率
            data['net_in'] = net_in
            data['net_out'] = net_out
        res = BaseResponse()
        res.data = data
        return res.dict


api.add_resource(HomeView, "/home", endpoint="home")
