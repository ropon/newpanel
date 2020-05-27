#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

Check_domain() {
	while [ -z $domain ] ;do
		Echo "msg" "请输入域名,比如www.ropon.top"
		read -p ": " domain
		#domain=`echo $domain|egrep '^([A-Za-z0-9*]{1,100}\.){1,8}([A-Za-z0-9]){1,24}$'`
		domain=$(echo $domain|egrep '^([A-Za-z0-9*]{1,100}\.){1,8}([A-Za-z0-9]){1,24}$')
	done
	conffile=$(grep -l " $domain" ${NgDirs[VhostDir]}/*.conf) >/dev/null 2>&1
	[ -f "$conffile" ] && Echo "warning" "${domain}绑定到${conffile}文件中" && exit
}

Vhost() {
	Check_domain
	[ -d ${NgDirs[WwwrootDir]}/${domain} ] && mv ${NgDirs[WwwrootDir]}/${domain}{,`date +%Y%m%d%H%M`} || mkdir -p ${NgDirs[WwwrootDir]}/${domain}
	wget -O ${NgDirs[VhostDir]}/.${domain}_temp.conf http://panel.ropon.top/panel/lnmp/config/vhost.txt && sed -i "s@test.ropon.top@$domain@g" ${NgDirs[VhostDir]}/.${domain}_temp.conf
	Echo "msg" "是否再绑定其他域名,请输入[y/n]"
	read -p ": " is_bdomain
	while [[ ! $is_bdomain =~ ^[y,n]$ ]] ;do
		Echo "warning" "输入有误,只能输入[y/n]"
		read -p "[y/n]: " is_bdomain
	done
	[ "$is_bdomain" == 'y' ] && Check_domain && echo "test"
	${NgDirs[NginxInstallDir]}/sbin/nginx -t
	if [ $? -eq 0 ] ;then
		mv ${NgDirs[VhostDir]}/.${domain}_temp.conf{,${domain}.conf}
		service nginxd reload
		Echo "success" "创建站点成功"
	else
		rm -f ${NgDirs[VhostDir]}/.${domain}_temp.conf
		Echo "failure" "创建站点失败"
	fi
}

Main() {
	. ./config.conf
	Vhost
}

Main
