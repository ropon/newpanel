#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

[ ! -z $1 ] && MysqlVer=$1

Main() {
	pushd /home/panel/newpanel/shell
	. ./config.conf
	CheckOS
	[ $CentOSVer -ne 7 ] && Echo "warning" "暂时仅支持Centos7.x" && exit
	. include/mysql.sh && [ -d "${MysqlDirs[MysqlInstallDir]}/support-files" ] && Echo "warning" "${MysqlFiles[mysql]}安装成功" || Mysql
	popd
}

Main
