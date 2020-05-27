#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

InstallNginx() {
	pushd $BaseDir
	# 批量下载并解压所需包
	for key in ${!NgFiles[*]}; do
		[ ! -f ${NgFiles[$key]}.tar.gz ] && Download ${MirrorLink}/${NgFiles[$key]}.tar.gz
		[ ! -d ${NgFiles[$key]} ] && tar xzf ${NgFiles[$key]}.tar.gz
    done
	# 批量检测并创建所需目录
	for key in ${!NgDirs[*]}; do
		[ ! -d "${NgDirs[$key]}" ] && mkdir -p ${NgDirs[$key]}
    done

	id -u $RunUser >/dev/null 2>&1
	[ $? -ne 0 ] && useradd -M -s /sbin/nologin $RunUser
	pushd ${NgFiles[nginx]}
	./configure --prefix=${NgDirs[NginxInstallDir]} --user=$RunUser --group=$RunUser --with-http_stub_status_module --with-http_v2_module --with-http_ssl_module \
	--with-http_gzip_static_module --with-http_realip_module --with-http_flv_module --with-http_mp4_module --with-pcre=../${NgFiles[pcre]} \
	--with-openssl=../${NgFiles[openssl]} --with-zlib=../${NgFiles[zlib]} --with-pcre-jit $NginxModulesOptions 
	make -j${Thread} && make install
	
	if [ -f "${NgDirs[NginxInstallDir]}/conf/nginx.conf" ]; then
		# 创建软链接
		[ -d "$nginxpath" ] && mv ${nginxpath}{,_bak}
		ln -sf ${NgDirs[NginxInstallDir]} ${nginxpath}
		Echo "success" "${NgFiles[nginx]}安装成功"	
	else
		rm -rf ${NgDirs[NginxInstallDir]}
		Echo "failure" "${NgFiles[nginx]}安装失败" && exit
	fi
	# 判断加path
	[ -z "`grep ^'export PATH=' /etc/profile`" ] && echo "export PATH=${NgDirs[NginxInstallDir]}/sbin:\$PATH" >> /etc/profile
	[ -n "`grep ^'export PATH=' /etc/profile`" -a -z "`grep ${NgDirs[NginxInstallDir]} /etc/profile`" ] && sed -i "s@^export PATH=\(.*\)@export PATH=${NgDirs[NginxInstallDir]}/sbin:\1@" /etc/profile
	sleep 1
	. /etc/profile
	if [ -e /bin/systemctl ]; then
		wget -O /lib/systemd/system/nginxd.service http://panel.ropon.top/panel/lnmp/init.d/nginxd.service.txt
		sed -i "s@/usr/local/nginx@${NgDirs[NginxInstallDir]}@g" /lib/systemd/system/nginxd.service
		systemctl enable nginxd
	else
		[ "$OS" == "CentOS" ] && { wget -O /etc/init.d/nginxd http://panel.ropon.top/panel/lnmp/init.d/nginxd.txt; chkconfig --add nginxd; chkconfig nginxd on; chmod +x /etc/init.d/nginxd; }
		sed -i "s@/usr/local/nginx@${NgDirs[NginxInstallDir]}@g" /etc/init.d/nginxd
	fi
	cp ${NgDirs[NginxInstallDir]}/conf/nginx.conf{,_bk}
	wget -O ${NgDirs[NginxInstallDir]}/conf/nginx.conf http://panel.ropon.top/panel/lnmp/config/nginx.txt
	sed -i "s@/data/wwwroot/default@${NgDirs[DefaultDir]}@" ${NgDirs[NginxInstallDir]}/conf/nginx.conf
	sed -i "s@/data/wwwlogs@${NgDirs[WwwlogsDir]}@g" ${NgDirs[NginxInstallDir]}/conf/nginx.conf
	sed -i "s@^user www www@user $RunUser $RunUser@" ${NgDirs[NginxInstallDir]}/conf/nginx.conf
	#配置日志自动切割
	wget -O /etc/logrotate.d/nginx http://panel.ropon.top/panel/lnmp/config/nginxlogs.txt
	sed -i "s@/data/wwwlogs@${NgDirs[WwwlogsDir]}@g" /etc/logrotate.d/nginx
	ln -sf ${NgDirs[VhostDir]} ${NgDirs[NginxInstallDir]}/conf/vhost
	wget -O ${NgDirs[DefaultDir]}/index.html http://panel.ropon.top/panel/lnmp/config/index.txt
	sleep 1
	wget -O ${NgDirs[DefaultDir]}/phpinfo.php http://panel.ropon.top/panel/lnmp/config/phpinfo.txt
	sleep 1
	popd
	[ ! -f ${NgDirs[phpMyAdminDir]}/index.php ] && /bin/cp -r ${BaseDir}/${NgFiles[phpMyAdmin]}/* ${NgDirs[phpMyAdminDir]}
	chown $RunUser:$RunUser -R ${NgDirs[WwwrootDir]}
	chmod 744 -R ${NgDirs[WwwrootDir]}
	# 批量清理下载文件及解压后文件夹
	for key in ${!NgFiles[*]};do
		rm -rf ${NgFiles[$key]}.tar.gz ${NgFiles[$key]}
	done
	popd
	ldconfig
	service nginxd start
}

Nginx() {
	if [ -z $NginxVer ]; then
		Echo "msg" "跳过安装Nginx"
	else
		Echo "msg" "正在安装Nginx${NginxVer}"
		yum install -y gcc-c++ perl pcre-devel openssl openssl-devel
		InstallNginx
	fi
}
