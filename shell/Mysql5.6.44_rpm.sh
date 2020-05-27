#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top


Main() {
	pushd /home/panel/newpanel/shell
	. ./config.conf
	CheckOS
	[ $CentOSVer -ne 7 ] && Echo "warning" "暂时仅支持Centos7.x" && exit
	yum install gcc-c++ perl ncurses ncurses-devel libaio numactl numactl-libs perl-Module-Install -y
	if [ $? -eq 0 ]; then
		Download http://panel.ropon.top/rpm/MySQL-5.6.44-1.el7.x86_64.rpm
		rpm -ivh MySQL-5.6.44-1.el7.x86_64.rpm
		[ $? -eq 0 ] && rm -rf MySQL-5.6.44-1.el7.x86_64.rpm && Echo "success" "MySQL-5.6.44 安装成功"	
	fi
	popd
}

Main
