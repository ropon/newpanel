#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/2 15:36
# @Author  : Ropon
# @File    : ftp.py

import os
from api.utils.tools import execShell


class PanelFtp(object):

    def __init__(self):
        self._ftp_bin = "/usr/local/ftp/bin"

    def check(self):
        if not os.path.exists(self._ftp_bin):
            return "还没安装ftp服务,请先安装"
        if int(execShell("ps aux|grep pure-ftpd|grep -v grep|wc -l")) == 0:
            return "还没启动ftp服务,请先启动"

    def checkpathisexists(self, path):
        if not os.path.exists(path):
            execShell(f"mkdir -p {path}")
            execShell(f"chown -R www.www {path}")
            execShell(f"chmod -R 744 {path}")

    def reloadftp(self):
        execShell(f"{self._ftp_bin}/pure-pw mkdb /usr/local/ftp/etc/pureftpd.pdb")

    def create_ftp(self, ftp_user=None, ftp_passwd=None, ftp_path=None):
        self.checkpathisexists(ftp_path)
        execShell(
            f"{self._ftp_bin}/pure-pw useradd {ftp_user} -u www -d {ftp_path} -m <<EOF \n{ftp_passwd}\n{ftp_passwd}\nEOF")
        self.reloadftp()

    def delete_ftp(self, ftp_user=None, ftp_path=None):
        execShell(f"{self._ftp_bin}/pure-pw userdel {ftp_user}")
        if os.path.exists(ftp_path):
            # pass
            # 删除FTP根目录
            execShell(f"/usr/bin/rm -rf {ftp_path}")
        self.reloadftp()

    def update_ftp(self, status=None, ftp_user=None, ftp_passwd=None):
        # 修改状态
        if status is not None:
            if status == 0:
                execShell(f"{self._ftp_bin}/pure-pw usermod {ftp_user} -r 1")
            else:
                execShell(f"{self._ftp_bin}/pure-pw usermod {ftp_user} -r ''")
        # 修改密码
        if ftp_passwd is not None:
            execShell(f"{self._ftp_bin}/pure-pw passwd {ftp_user} <<EOF \n{ftp_passwd}\n{ftp_passwd}\nEOF")
        self.reloadftp()
