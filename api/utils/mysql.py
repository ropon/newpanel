#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/2 15:36
# @Author  : Ropon
# @File    : mysql.py

import os
import pymysql
from api.utils.tools import execShell


class PanelMysql(object):

    def __init__(self, user, passwd, dbname, host="localhost", port=3306, charset="utf8"):
        self._user = user
        self._passwd = passwd
        self._dbname = dbname
        self._host = host
        self._port = port
        self._charset = charset
        self._conn = None
        self._cursor = None
        self._error = None
        self._mysqlpath = "/usr/local/mysql/bin"

    # 创建连接
    def _conn_db(self):
        params = {
            "user": self._user,
            "password": self._passwd,
            "db": self._dbname,
            "host": self._host,
            "port": self._port,
            "charset": self._charset
        }
        try:
            self._conn = pymysql.connect(**params)
            self._cursor = self._conn.cursor()
        except pymysql.Error as e:
            self._error = e

    def check(self):
        if not os.path.exists(self._mysqlpath):
            return "还没安装mysql服务,请先安装"
        if int(execShell("ps aux|grep mysql|grep -v grep|wc -l")) == 0:
            return "还没启动mysql服务,请先启动"
        self._conn_db()
        if self._error:
            return "root登录失败,请检查root密码配置"

    # 关闭连接
    def _close_db(self):
        self._cursor.close()
        self._conn.close()

    def execute(self, sql):
        self._conn_db()
        try:
            result = self._cursor.execute(sql)
            self._conn.commit()
            self._close_db()
            return result
        except Exception as e:
            return e

    def create_mysql(self, mysql_user=None, mysql_passwd=None, mysql_name=None, accept=None):
        result = ""
        create_user_sql = "CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (mysql_user, accept, mysql_passwd)
        flush_sql = "flush privileges;"
        try:
            self.execute(create_user_sql)
            self.execute(flush_sql)
            result = result + f"用户:{mysql_user}创建成功"
        except Exception as e:
            result = result + str(e)

        create_mysql_sql = "CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8mb4;" % mysql_name
        try:
            self.execute(create_mysql_sql)
            result = result + f"数据库:{mysql_name}创建成功"
        except Exception as e:
            result = result + str(e)

        grant_user_sql = "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s';" % (mysql_name, mysql_user, accept)
        try:
            self.execute(grant_user_sql)
            result = result + f"对数据库:{mysql_name} 赋给用户:{mysql_user}所有权限"
        except Exception as e:
            result = result + str(e)
        return result

    def delete_mysql(self, mysql_user=None, mysql_name=None, accept=None):
        result = ""
        delete_user_sql = "DROP USER '%s'@'%s';" % (mysql_user, accept)
        flush_sql = "flush privileges;"
        try:
            self.execute(delete_user_sql)
            self.execute(flush_sql)
            result = result + f"用户:{mysql_user}删除成功"
        except Exception as e:
            result = result + str(e)

        delete_mysql_sql = "DROP DATABASE %s;" % mysql_name
        try:
            self.execute(delete_mysql_sql)
            result = result + f"数据库:{mysql_name}删除成功"
        except Exception as e:
            result = result + str(e)
        return result

    def update_mysql(self, mysql_user=None, old_passwd=None, mysql_passwd=None, mysql_name=None, accept=None,
                     old_accept=None):
        result = ""
        flush_sql = "flush privileges;"

        if accept and accept != old_accept:
            # 取消授权
            cancel_grant_sql = "REVOKE ALL ON %s.* FROM '%s'@'%s';" % (mysql_name, mysql_user, old_accept)
            # 删除原用户
            delete_user_sql = "DROP USER '%s'@'%s';" % (mysql_user, old_accept)
            if mysql_passwd:
                old_passwd = mysql_passwd
            grant_user_sql = "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s' IDENTIFIED BY '%s';" % (
                mysql_name, mysql_user, accept, old_passwd)
            try:
                self.execute(cancel_grant_sql)
                self.execute(delete_user_sql)
                self.execute(grant_user_sql)
                self.execute(flush_sql)
                result = result + f"用户:{mysql_user}修改连接为{accept},密码更新为{old_passwd}"
            except Exception as e:
                result = result + str(e)
        else:
            if mysql_passwd:
                update_user_sql = "SET PASSWORD FOR '%s'@'%s'=Password('%s');" % (mysql_user, old_accept, mysql_passwd)
                try:
                    self.execute(update_user_sql)
                    self.execute(flush_sql)
                    result = result + f"用户:{mysql_user}修改密码成功"
                except Exception as e:
                    result = result + str(e)
        return result
