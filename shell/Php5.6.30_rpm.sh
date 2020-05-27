#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

Main() {
	pushd /home/panel/newpanel/shell
	. ./config.conf
	CheckOS
	[ $CentOSVer -ne 7 ] && Echo "warning" "暂时仅支持Centos7.x" && exit
	Echo "warning" "暂时不支持"
	popd
}

Main
