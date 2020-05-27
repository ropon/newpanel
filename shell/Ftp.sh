#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

[ ! -z $1 ] && FtpVer=$1

Main() {
	pushd /home/panel/newpanel/shell
	. ./config.conf
	CheckOS
	[ $CentOSVer -ne 7 ] && Echo "warning" "暂时仅支持Centos7.x" && exit
	. include/ftp.sh && [ -e "${FtpDirs[FtpInstallDir]}/sbin/pure-ftpwho" ] && Echo "warning" "${FtpFiles[ftp]}安装成功" || Ftp
	popd
}

Main
