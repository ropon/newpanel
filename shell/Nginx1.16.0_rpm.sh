#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

Main() {
	pushd /home/panel/newpanel/shell
	. ./config.conf
	CheckOS
	[ $CentOSVer -ne 7 ] && Echo "warning" "暂时仅支持Centos7.x" && exit
	yum install gcc-c++ pcre-devel openssl-devel -y
	[ ! -f nginx-1.16.0-1.el7.x86_64.rpm ] && Download ${MirrorLink}/nginx-1.16.0-1.el7.x86_64.rpm 
	rpm -ivh nginx-1.16.0-1.el7.x86_64.rpm
	[ $? -eq 0 ] && rm -rf nginx-1.16.0-1.el7.x86_64.rpm
	Echo "success" "nginx-1.16.0 安装成功"
	popd
}

Main
