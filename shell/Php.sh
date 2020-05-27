#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

[ ! -z $1 ] && PhpVer=$1

Main() {
	pushd /home/panel/newpanel/shell
	. ./config.conf
	CheckOS
	[ $CentOSVer -ne 7 ] && Echo "warning" "暂时仅支持Centos7.x" && exit
	. include/php.sh && [ -f "${PhpDirs[PhpInstallDir]}/bin/phpize" ] && Echo "warning" "${PhpFiles[php]}已安装成功" || Php
	popd
}

Main
