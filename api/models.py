#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/1 15:24
# @Author  : Ropon
# @File    : models.py

import datetime, json
from api import db
from werkzeug.security import generate_password_hash, check_password_hash


class SysConf(db.Model):
    __tablename__ = "sysconf"
    __table_args__ = {"useexisting": True}
    nid = db.Column(db.Integer, primary_key=True)
    webserver = db.Column(db.String(64))
    www_path = db.Column(db.String(256))
    logs_path = db.Column(db.String(256))
    bkup_path = db.Column(db.String(256))
    mysql_root = db.Column(db.String(256))

    @classmethod
    def update(cls, nid, update_dict):
        cls.query.filter_by(nid=nid).update(update_dict)
        return session_commit()


class Site(db.Model):
    __tablename__ = "site"
    __table_args__ = {"useexisting": True}
    nid = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(64), unique=True)
    root_path = db.Column(db.String(256))
    bind_domain = db.Column(db.String(256))
    status = db.Column(db.Boolean, default=1)
    note = db.Column(db.Text(), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def to_json(self):
        json_site = {
            "nid": self.nid,
            "site_name": self.site_name,
            "root_path": self.root_path,
            "bind_domain": self.bind_domain,
            "status": self.status,
            "status_text": ("开启" if (self.status) else "关闭"),
            "note": self.note,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S")
        }
        return json_site

    def add(self):
        db.session.add(self)
        return session_commit()

    @classmethod
    def delete(cls, nid):
        cls.query.filter_by(nid=nid).delete()
        return session_commit()

    @classmethod
    def update(cls, nid, update_dict):
        cls.query.filter_by(nid=nid).update(update_dict)
        return session_commit()

    @classmethod
    def get(cls, nid):
        return cls.query.filter_by(nid=nid).first()

    @classmethod
    def search(cls, extra, bind_domain, page, num):
        sites_temp = cls.query.filter_by(**extra)
        if bind_domain:
            sites_temp = sites_temp.filter(cls.bind_domain.contains(bind_domain))
        return sites_temp.paginate(page, num, error_out=False)


class SiteInfo(db.Model):
    __tablename__ = "siteinfo"
    __table_args__ = {"useexisting": True}
    extra_kwargs_dict = {"rewrite": "", "set_301": False, "set_404": False, "deny_ua": True, "deny_referer": True,
                         "safe": True,
                         "cache": True}
    nid = db.Column(db.Integer, primary_key=True)
    port = db.Column(db.Integer(), default=80)
    is_ssl = db.Column(db.Boolean, default=0)
    php_ver = db.Column(db.String(64), default="php7.0")
    default_index = db.Column(db.String(256),
                              default="index.php index.html index.htm default.php default.htm default.html")
    is_log = db.Column(db.Boolean, default=0)
    log_path = db.Column(db.String(256))
    domain_301 = db.Column(db.String(256))
    extra_kwargs = db.Column(db.Text(),
                             default=json.dumps(extra_kwargs_dict))
    sslcrt = db.Column(db.Text(), nullable=True, default="")
    sslkey = db.Column(db.Text(), nullable=True, default="")
    site_id = db.Column(db.Integer, db.ForeignKey("site.nid"))
    siteinfo2site = db.relationship("Site", backref="site2siteinfo", uselist=False)

    def to_json(self):
        json_siteinfo = {
            "nid": self.nid,
            "port": self.port,
            "is_ssl": self.is_ssl,
            "php_ver": self.php_ver,
            "default_index": self.default_index,
            "is_log": self.is_log,
            "log_path": self.log_path,
            "domain_301": self.domain_301,
            "extra_kwargs": json.loads(self.extra_kwargs),
            "sslcrt": self.sslcrt,
            "sslkey": self.sslkey
        }
        return json_siteinfo

    def add(self):
        db.session.add(self)
        return session_commit()

    @classmethod
    def sdelete(cls, site_id):
        cls.query.filter_by(site_id=site_id).delete()
        return session_commit()

    @classmethod
    def supdate(cls, nid, update_dict):
        cls.query.filter_by(site_id=nid).update(update_dict)
        return session_commit()

    @classmethod
    def sget(cls, nid):
        return cls.query.filter_by(site_id=nid).first()


class Ftp(db.Model):
    __tablename__ = "ftp"
    __table_args__ = {"useexisting": True}
    nid = db.Column(db.Integer, primary_key=True)
    ftp_user = db.Column(db.String(64), unique=True)
    ftp_passwd = db.Column(db.String(256))
    ftp_path = db.Column(db.String(256))
    status = db.Column(db.Boolean, default=1)
    note = db.Column(db.Text(), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def to_json(self):
        json_ftp = {
            "nid": self.nid,
            "ftp_user": self.ftp_user,
            "ftp_passwd": self.ftp_passwd,
            "ftp_path": self.ftp_path,
            "status": self.status,
            "status_text": ("开启" if (self.status) else "关闭"),
            "note": self.note,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S")
        }
        return json_ftp

    def add(self):
        db.session.add(self)
        return session_commit()

    @classmethod
    def delete(cls, nid):
        cls.query.filter_by(nid=nid).delete()
        return session_commit()

    @classmethod
    def update(cls, nid, update_dict):
        cls.query.filter_by(nid=nid).update(update_dict)
        return session_commit()

    @classmethod
    def get(cls, nid):
        return cls.query.filter_by(nid=nid).first()

    @classmethod
    def search(cls, extra, page, num):
        return cls.query.filter_by(**extra).paginate(page, num, error_out=False)


class Mysql(db.Model):
    __tablename__ = "mysql"
    __table_args__ = {"useexisting": True}
    nid = db.Column(db.Integer, primary_key=True)
    mysql_user = db.Column(db.String(64))
    mysql_name = db.Column(db.String(64))
    mysql_passwd = db.Column(db.String(256))
    accept = db.Column(db.String(64), default="localhost")
    status = db.Column(db.Boolean, default=1)
    note = db.Column(db.Text(), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def to_json(self):
        json_mysql = {
            "nid": self.nid,
            "mysql_user": self.mysql_user,
            "mysql_name": self.mysql_name,
            "mysql_passwd": self.mysql_passwd,
            "accept": self.accept,
            "status": self.status,
            "note": self.note,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S")
        }
        return json_mysql

    def add(self):
        db.session.add(self)
        return session_commit()

    @classmethod
    def delete(cls, nid):
        cls.query.filter_by(nid=nid).delete()
        return session_commit()

    @classmethod
    def update(cls, nid, update_dict):
        cls.query.filter_by(nid=nid).update(update_dict)
        return session_commit()

    @classmethod
    def get(cls, nid):
        return cls.query.filter_by(nid=nid).first()

    @classmethod
    def search(cls, extra, page, num):
        return cls.query.filter_by(**extra).paginate(page, num, error_out=False)


class Soft(db.Model):
    __tablename__ = "soft"
    __table_args__ = {"useexisting": True}
    nid = db.Column(db.Integer, primary_key=True)
    soft_name = db.Column(db.String(64))
    soft_ver = db.Column(db.String(64))
    soft_desc = db.Column(db.Text(), nullable=True)
    is_install = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def to_json(self):
        json_soft = {
            "nid": self.nid,
            "soft_name": self.soft_name,
            "soft_ver": self.soft_ver,
            "soft_desc": self.soft_desc,
            "is_install": self.is_install,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S")
        }
        return json_soft

    def add(self):
        db.session.add(self)
        return session_commit()

    @classmethod
    def delete(cls, nid):
        cls.query.filter_by(nid=nid).delete()
        return session_commit()

    @classmethod
    def update(cls, nid, update_dict):
        cls.query.filter_by(nid=nid).update(update_dict)
        return session_commit()

    @classmethod
    def get(cls, nid):
        return cls.query.filter_by(nid=nid).first()

    @classmethod
    def search(cls, extra, page, num):
        return cls.query.filter_by(**extra).paginate(page, num, error_out=False)


class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"useexisting": True}
    nid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256))
    password = db.Column(db.String(256))
    status = db.Column(db.Boolean, default=0)
    errtimes = db.Column(db.Integer)
    locktime = db.Column(db.DateTime, default=datetime.datetime.now)

    @classmethod
    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, hash, password):
        return check_password_hash(hash, password)

    def add(self):
        db.session.add(self)
        return session_commit()

    @classmethod
    def update(cls, nid, update_dict):
        cls.query.filter_by(nid=nid).update(update_dict)
        return session_commit()

    @classmethod
    def get(cls, nid):
        return cls.query.filter_by(nid=nid).first()

    @classmethod
    def updateplus(cls, nid):
        cls.query.filter_by(nid=nid).update({cls.errtimes: cls.errtimes + 1},
                                            synchronize_session="evaluate")
        return session_commit()


class Token(db.Model):
    __tablename__ = "token"
    __table_args__ = {"useexisting": True}
    nid = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(256))
    created = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.nid"))
    token2user = db.relationship("User", backref="user2token", uselist=False)

    def add(self):
        db.session.add(self)
        return session_commit()

    @classmethod
    def uupdate(cls, user_id, update_dict):
        cls.query.filter_by(user_id=user_id).update(update_dict)
        return session_commit()

    @classmethod
    def uget(cls, user_id):
        return cls.query.filter_by(user_id=user_id).first()


def session_commit():
    try:
        db.session.commit()
    except db.SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        print(reason)
        return reason
