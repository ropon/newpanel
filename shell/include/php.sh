#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

InstallPhp() {
	pushd $BaseDir
	# 批量检测并创建所需目录
	for key in ${!PhpDirs[*]};do
		[ ! -d "${PhpDirs[$key]}" ] && mkdir -p ${PhpDirs[$key]}
    done

	id -u $RunUser >/dev/null 2>&1
	[ $? -ne 0 ] && useradd -M -s /sbin/nologin $RunUser
	
	which iconv >/dev/null 2>&1
	if [ $? -ne 0 ]; then
		[ ! -f ${PhpFiles[libiconv]}.tar.gz ] && Download ${MirrorLink}/${PhpFiles[libiconv]}.tar.gz
		[ ! -d ${PhpFiles[libiconv]} ] && tar xzf ${PhpFiles[libiconv]}.tar.gz
		pushd ${PhpFiles[libiconv]}
		./configure --prefix=${PhpDirs[LibiconvInstallDir]}
		make -j ${THREAD} && make install
		popd
	fi
	
	if [ $PhpVer == "7.3.1" ]; then
		which cmake >/dev/null 2>&1
		[ $? -eq 0 ] && yum remove -y cmake 
		[ ! -f ${PhpFiles[cmake]}.tar.gz ] && Download ${MirrorLink}/${PhpFiles[cmake]}.tar.gz
		[ ! -d ${PhpFiles[cmake]} ] && tar xzf ${PhpFiles[cmake]}.tar.gz
		pushd ${PhpFiles[cmake]}
		./configure
		make -j${Thread} && make install
		popd
		yum remove -y libzip libzip-devel
		[ ! -f ${PhpFiles[libzip]}.tar.gz ] && Download ${MirrorLink}/${PhpFiles[libzip]}.tar.gz
		[ ! -d ${PhpFiles[libzip]} ] && tar xzf ${PhpFiles[libzip]}.tar.gz
		pushd ${PhpFiles[libzip]}
		mkdir build && pushd build && cmake .. && make -j${Thread} && make install && popd
		popd
		echo '/usr/local/lib64
		/usr/local/lib
		/usr/lib
		/usr/lib64'>>/etc/ld.so.conf && ldconfig -v
	fi
	
	[ ! -f ${PhpFiles[php]}.tar.gz ] && Download ${MirrorLink}/${PhpFiles[php]}.tar.gz
	[ ! -d ${PhpFiles[php]} ] && tar xzf ${PhpFiles[php]}.tar.gz
	pushd ${PhpFiles[php]}
	./configure --prefix=${PhpDirs[PhpInstallDir]} --with-config-file-path=${PhpDirs[PhpInstallDir]}/etc --with-config-file-scan-dir=${PhpDirs[PhpInstallDir]}/etc/php.d \
	--with-fpm-user=$RunUser --with-fpm-group=$RunUser --enable-fpm --disable-opcache --disable-fileinfo --with-mysql=mysqlnd --with-mysqli=mysqlnd \
	--with-pdo-mysql=mysqlnd --with-iconv-dir=${PhpDirs[LibiconvInstallDir]} --with-freetype-dir --with-jpeg-dir --with-png-dir --with-zlib --with-libxml-dir --enable-xml \
	--disable-rpath --enable-bcmath --enable-shmop --enable-exif --enable-sysvsem --enable-inline-optimization --with-curl=/usr/local --enable-mbregex --enable-mbstring \
	--with-mcrypt --with-gd --enable-gd-native-ttf --with-openssl --with-mhash --enable-pcntl --enable-sockets --with-xmlrpc --enable-ftp --enable-intl --with-xsl --with-gettext \
	--enable-zip --enable-soap --disable-debug $PhpModulesOptions
	make -j${Thread} && make install
	
	if [ -f "${PhpDirs[PhpInstallDir]}/bin/phpize" ]; then
		# 创建软链接
		[ -d "$phppath" ] && mv ${phppath}{,_bak}
		ln -sf ${PhpDirs[PhpInstallDir]} ${phppath}
		Echo "success" "${PhpFiles[php]}安装成功"	
	else
		rm -rf ${PhpDirs[PhpInstallDir]}
		Echo "failure" "${PhpFiles[php]}安装失败" && exit
	fi
	# 判断加path
	[ -z "`grep ^'export PATH=' /etc/profile`" ] && echo "export PATH=${PhpDirs[PhpInstallDir]}/bin:\$PATH" >> /etc/profile
	[ -n "`grep ^'export PATH=' /etc/profile`" -a -z "`grep ${PhpDirs[PhpInstallDir]} /etc/profile`" ] && sed -i "s@^export PATH=\(.*\)@export PATH=${PhpDirs[PhpInstallDir]}/bin:\1@" /etc/profile
	sleep 1
	. /etc/profile
	
	/bin/cp php.ini-production ${PhpDirs[PhpInstallDir]}/etc/php.ini
	sed -i 's@^;date.timezone.*@date.timezone = Asia/Shanghai@' ${PhpDirs[PhpInstallDir]}/etc/php.ini
	sed -i 's@^short_open_tag = Off@short_open_tag = On@' ${PhpDirs[PhpInstallDir]}/etc/php.ini
	sed -i 's@^post_max_size.*@post_max_size = 100M@' ${PhpDirs[PhpInstallDir]}/etc/php.ini
	sed -i 's@^upload_max_PhpFilesize.*@upload_max_PhpFilesize = 50M@' ${PhpDirs[PhpInstallDir]}/etc/php.ini
	sed -i 's@^max_execution_time.*@max_execution_time = 300@' ${PhpDirs[PhpInstallDir]}/etc/php.ini
	sed -i 's@^disable_functions.*@disable_functions = passthru,exec,system,chroot,chgrp,chown,shell_exec,proc_open,proc_get_status,ini_alter,ini_restore,dl,openlog,syslog,readlink,symlink,popepassthru,stream_socket_server,fsocket,popen@' ${PhpDirs[PhpInstallDir]}/etc/php.ini
	
	/bin/cp sapi/fpm/init.d.php-fpm /etc/init.d/php${PhpFlag}-fpm
	sed -i "s@php-fpm.pid@php${PhpFlag}-fpm.pid@" /etc/init.d/php${PhpFlag}-fpm
	chmod +x /etc/init.d/php${PhpFlag}-fpm
	chkconfig --add php${PhpFlag}-fpm && chkconfig php${PhpFlag}-fpm on
	wget -O ${PhpDirs[PhpInstallDir]}/etc/php-fpm.conf http://panel.ropon.top/panel/lnmp/config/php-fpm.txt
	sed -i "s@www@$RunUser@" ${PhpDirs[PhpInstallDir]}/etc/php-fpm.conf
	sed -i "s@php@php${PhpFlag}@" ${PhpDirs[PhpInstallDir]}/etc/php-fpm.conf
		
	service php${PhpFlag}-fpm start
	sed -i "s@php.*-cgi@php${PhpFlag}-cgi@" ${NgDirs[NginxInstallDir]}/conf/nginx.conf
	service nginxd reload
	popd
	# 批量清理下载文件及解压后文件夹
	for key in ${!PhpFiles[*]};do
		rm -rf ${PhpFiles[$key]}.tar.gz ${PhpFiles[$key]}
	done
	popd	
}

Php() {
	if [ -z $PhpVer ]; then
		Echo "msg" "跳过安装Php"
	else
		Echo "msg" "正在安装Php${PhpVer}"
		yum install -y gcc-c++ libxml2-devel openssl-devel libcurl-devel gd-devel libmcrypt-devel libxslt-devel mhash mcrypt icu libicu libicu-devel
		InstallPhp
	fi
}
