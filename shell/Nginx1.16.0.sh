#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

Main() {
	. ./config.conf
	CheckOS
	[ $CentOSVer -ne 7 ] && Echo "warning" "暂时仅支持Centos7.x" && exit
	. include/nginx.sh && [ -f "${NgDirs[NginxInstallDir]}/conf/nginx.conf" ] && Echo "warning" "${NgFiles[nginx]}已成功安装成功" || Nginx
}

Main
