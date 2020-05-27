#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

#一键安装nginx php mysql ftp panel
#nginx默认安装版本是1.14.2
#启动方式 service nginxd start|stop|restart
#php支持版本 5.6.40 7.0.33 7.1.26 7.2.14 7.3.1
#启动方式 比如安装5.6.40 使用service php56-fpm start|stop|restart 其他同理
#mysql支持版本 5.5.62 5.6.43 5.7.25
#启动方式 service mysqld start|stop|restart 其他同理

#主函数
Main() {
	startTime=`date +%s`
	. ./config.conf
	CheckOS
	[ $CentOSVer -ne 7 ] && Echo "warning" "暂时仅支持Centos7.x" && exit
	. include/InitCentos.sh && [ -f "/root/.InitCentos.log" ] && Echo "warning" "已执行优化脚本" || Centos7 
	[ $? -eq 0 ] && . include/nginx.sh && [ -f "${NgDirs[NginxInstallDir]}/conf/nginx.conf" ] && Echo "warning" "${NgFiles[nginx]}已成功安装成功" || Nginx
	[ $? -eq 0 ] && . include/php.sh && [ -f "${PhpDirs[PhpInstallDir]}/bin/phpize" ] && Echo "warning" "${PhpFiles[php]}已安装成功" || Php
	[ $? -eq 0 ] && . include/mysql.sh && [ -d "${MysqlDirs[MysqlInstallDir]}/support-files" ] && Echo "warning" "${MysqlFiles[mysql]}安装成功" || Mysql
	[ $? -eq 0 ] && . include/ftp.sh && [ -e "${FtpDirs[FtpInstallDir]}/sbin/pure-ftpwho" ] && Echo "warning" "${FtpFiles[ftp]}安装成功" || Ftp
	[ $? -eq 0 ] && . include/panel.sh && [ -d "${PanelDirs[PanelInstallDir]}/.py3env" ] && Echo "warning" "${PanelFiles[panel]}安装成功" || Panel
	endTime=`date +%s`
	((installTime=($endTime-$startTime)/60))
	Echo "msg" "安装所需时间:${installTime}分钟"
	Echo "msg" "建议重启下服务器,是否重启服务器,请输入[y/n]"
	read -p ": " is_reboot
	while [[ ! $is_reboot =~ ^[y,n]$ ]] 
	do
		Echo "warning" "输入有误,只能输入[y/n]"
		read -p "[y/n]: " is_reboot
	done
	if [ "$is_reboot" == 'y' ];then
		reboot
	fi
}

Main
