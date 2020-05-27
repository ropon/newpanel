#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top

InstallFtp() {
	pushd $BaseDir
	# 批量下载并解压所需包
	for key in ${!FtpFiles[*]}; do
		[ ! -f ${FtpFiles[$key]}.tar.gz ] && Download ${MirrorLink}/${FtpFiles[$key]}.tar.gz
		[ ! -d ${FtpFiles[$key]} ] && tar xzf ${FtpFiles[$key]}.tar.gz
    done
	# 批量检测并创建所需目录
	for key in ${!FtpDirs[*]}; do
		[ ! -d "${FtpDirs[$key]}" ] && mkdir -p ${FtpDirs[$key]}
    done

	id -u $RunUser >/dev/null 2>&1
	[ $? -ne 0 ] && useradd -M -s /sbin/nologin $RunUser
	pushd ${FtpFiles[ftp]}
	./configure --prefix=${FtpDirs[FtpInstallDir]} CFLAGS=-O2 --with-puredb --with-quotas --with-cookie --with-virtualhosts \
	--with-virtualchroot --with-diraliases --with-sysquotas --with-ratios --with-altlog --with-paranoidmsg --with-shadow \
	--with-welcomemsg --with-throttling --with-uploadscript --with-language=english --with-rfc2640 $FtpModulesOptions
	make -j${Thread} && make install
	
	if [ -e "${FtpDirs[FtpInstallDir]}/bin/pure-pw" ]; then
		popd
		# 创建软链接
		[ -d "$ftppath" ] && mv ${ftppath}{,_bak}
		ln -sf ${FtpDirs[FtpInstallDir]} ${ftppath}
		# 批量清理下载文件及解压后文件夹
		for key in ${!FtpFiles[*]};do
			rm -rf ${FtpFiles[$key]}.tar.gz ${FtpFiles[$key]}
		done
		Echo "success" "${FtpFiles[ftp]}安装成功"	
	else
		rm -rf ${FtpDirs[FtpInstallDir]}
		Echo "failure" "${FtpFiles[ftp]}安装失败" && Exit
	fi
	# 判断加path
	[ -z "`grep ^'export PATH=' /etc/profile`" ] && echo "export PATH=${FtpDirs[FtpInstallDir]}/bin:\$PATH" >> /etc/profile
	[ -n "`grep ^'export PATH=' /etc/profile`" -a -z "`grep ${FtpDirs[FtpInstallDir]} /etc/profile`" ] && sed -i "s@^export PATH=\(.*\)@export PATH=${FtpDirs[FtpInstallDir]}/bin:\1@" /etc/profile
	sleep 1
	. /etc/profile
	
	if [ -e /bin/systemctl ]; then
		wget -O /lib/systemd/system/pureftp.service http://panel.ropon.top/panel/lnmp/init.d/pureftp.service.txt
		sed -i "s@/usr/local/nginx@${FtpDirs[FtpInstallDir]}@g" /lib/systemd/system/pureftp.service
		systemctl enable pureftp
	fi
	wget -O ${FtpDirs[FtpInstallDir]}/etc/pure-ftpd.conf http://panel.ropon.top/panel/lnmp/config/pure-ftpd.txt
	systemctl start pureftp
	popd
}

Ftp() {
	if [ -z $FtpVer ]; then
		Echo "msg" "跳过安装Ftp"
	else
		Echo "msg" "正在安装Ftp${FtpVer}"
		InstallFtp
	fi	
}
