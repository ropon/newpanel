#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

Main() {
	. ./config.conf
	CheckOS
	[ $CentOSVer -ne 7 ] && Echo "warning" "暂时仅支持Centos7.x" && exit
	. include/mysql.sh && [ -d "${MysqlDirs[MysqlInstallDir]}/support-files" ] && Echo "warning" "${MysqlFiles[mysql]}安装成功" || Mysql
}

Main
