#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/13 14:08
# @Author  : Ropon
# @File    : file.py

import os, time
from flask import Blueprint, request
from flask_restful import Api, Resource
from api.utils.response import BaseResponse, api_abort
from api.utils.config import www_path
from api.utils.tools import check
from api.utils.tools import execShell

file_bp = Blueprint("file_bp", __name__, url_prefix="/api/v1")
api = Api(file_bp)


class FileView(Resource):

    def readfile(self, filename, mode='r'):
        if not os.path.exists(filename): return False
        fp = open(filename, mode)
        f_body = fp.read()
        fp.close()
        return f_body

    def savefile(self, filename, content, mode="w"):
        try:
            fp = open(filename, mode)
            fp.write(content)
            fp.close()
            return True
        except:
            return False

    def get(self):
        basedir = www_path
        newdir = request.args.get("d", "")
        filename = request.args.get("file")
        res = BaseResponse()
        if filename:
            res.data = self.readfile(filename)
            return res.dict
        # check(obj_path=newdir)
        if newdir and os.path.isdir(os.path.join(basedir, newdir)):
            basedir = os.path.join(basedir, newdir)

        def convertime(timeStamp):
            timeArray = time.localtime(timeStamp)
            return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)

        def list_dir(path, ret):
            for i in os.listdir(path):
                temp_dir = os.path.join(path, i)
                if os.path.isdir(temp_dir):
                    file_dict = {
                        "type": "dir",
                        "name": i,
                        "ctime": convertime(os.path.getctime(temp_dir)),
                        "utime": convertime(os.path.getmtime(temp_dir))
                    }
                else:
                    temp_file = os.path.join(path, i)
                    file_dict = {
                        "type": "file",
                        "name": i,
                        "ctime": convertime(os.path.getctime(temp_file)),
                        "utime": convertime(os.path.getmtime(temp_file))
                    }
                ret.append(file_dict)
            return ret

        file_list = []
        res.basedir = basedir
        ress = list_dir(basedir, file_list)
        from operator import itemgetter
        ress_bytype = sorted(ress, key=itemgetter('type'))
        res.data = ress_bytype
        return res.dict

    def delete(self):
        filename = request.json.get("file")
        print(filename)
        execShell(f"/usr/bin/rm -rf {filename}")
        res = BaseResponse()
        return res.dict

    def put(self):
        filename = request.form.get("file")
        file_content = request.form.get('content')
        ret = self.savefile(filename, file_content)
        res = BaseResponse()
        if not ret:
            api_abort(httpcode=400, errcode=4025, key="文件保存失败")
        return res.dict


api.add_resource(FileView, "/file", endpoint="file")
