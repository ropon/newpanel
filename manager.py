#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/1 15:25
# @Author  : Ropon
# @File    : manager.py

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from api import create_app, db, models
from api.utils.tools import getRandomString

app = create_app()

manager = Manager(app)

Migrate(app, db)
manager.add_command("db", MigrateCommand)


# python manage.py shell
@manager.shell
def make_shell_context():
    return dict(
        SysConf=models.SysConf,
        User=models.User,
        user=models.User.query.filter_by(nid=1).first()
    )


@manager.command
def repasswd():
    ret = make_shell_context()
    User = ret.get('User')
    user = ret.get('user')
    username = getRandomString(slen=6)
    password = getRandomString()
    user_data = {'username': username, 'password': User.set_password(password), 'status': 1, 'errtimes': 0}
    if user:
        User.update(1, user_data)
    else:
        User(**user_data).add()
    print(f'username: {username}\npassword: {password}')


@manager.option('-r', '--rpasswd', help='mysql root password')
def rerootpwd(rpasswd):
    ret = make_shell_context()
    SysConf = ret.get('SysConf')
    SysConf.update(1, {'mysql_root': rpasswd})


if __name__ == '__main__':
    manager.run()
