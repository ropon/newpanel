#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top
RunUser=mysql

InstallMysql() {
	pushd $BaseDir
	[ "${MysqlVer}" == "5.7.25" ] && MysqlModulesOptions="-DWITH_BOOST=boost"
	#if [ "${MysqlVer}" == "8.0.14" ]; then
	#	[ ! -f ${MysqlFiles[boost]}.tar.gz ] && Download ${MirrorLink}/${MysqlFiles[boost]}.tar.gz
	#	[ ! -d ${MysqlFiles[boost]} ] && tar xzf ${MysqlFiles[boost]}.tar.gz
	#	MysqlModulesOptions="-DWITH_BOOST==../${MysqlFiles[boost]}"
	#fi

	# 批量检测并创建所需目录
	for key in ${!MysqlDirs[*]};do
		[ ! -d "${MysqlDirs[$key]}" ] && mkdir -p ${MysqlDirs[$key]}
    done

	id -u $RunUser >/dev/null 2>&1
	[ $? -ne 0 ] && useradd -M -s /sbin/nologin $RunUser
	
	which cmake >/dev/null 2>&1
	if [ $? -ne 0 ]; then
		[ ! -f ${MysqlFiles[cmake]}.tar.gz ] && Download ${MirrorLink}/${MysqlFiles[cmake]}.tar.gz
		[ ! -d ${MysqlFiles[cmake]} ] && tar xzf ${MysqlFiles[cmake]}.tar.gz
		pushd ${MysqlFiles[cmake]}
		./configure
		make -j${Thread} && make install
		popd
	fi
	[ ! -f ${MysqlFiles[mysql]}.tar.gz ] && Download ${MirrorLink}/${MysqlFiles[mysql]}.tar.gz
	[ ! -d ${MysqlFiles[mysql]} ] && tar xzf ${MysqlFiles[mysql]}.tar.gz
	pushd ${MysqlFiles[mysql]}
	cmake . -DCMAKE_INSTALL_PREFIX=${MysqlDirs[MysqlInstallDir]} -DMYSQL_DATADIR=${MysqlDirs[MysqlDataDir]} -DSYSCONFDIR=/etc $MysqlModulesOptions
	make -j${Thread} && make install
	
	if [ -d "${MysqlDirs[MysqlInstallDir]}/support-files" ]; then
		# 批量清理下载文件及解压后文件夹
		popd
		# 创建软链接
		[ -d "$mysqlpath" ] && mv ${mysqlpath}{,_bak}
		ln -sf ${MysqlDirs[MysqlInstallDir]} ${mysqlpath}
		for key in ${!MysqlFiles[*]};do
			rm -rf ${MysqlFiles[$key]}.tar.gz ${MysqlFiles[$key]}
		done
		Echo "success" "${MysqlFiles[mysql]}安装成功"	
	else
		rm -rf ${MysqlDirs[MysqlInstallDir]}
		Echo "failure" "${MysqlFiles[mysql]}安装失败" && exit
	fi
	
	/bin/cp ${MysqlDirs[MysqlInstallDir]}/support-files/mysql.server /etc/init.d/mysqld
	sed -i "s@^basedir=.*@basedir=${MysqlDirs[MysqlInstallDir]}@" /etc/init.d/mysqld
	sed -i "s@^datadir=.*@datadir=${MysqlDirs[MysqlDataDir]}@" /etc/init.d/mysqld
	chmod +x /etc/init.d/mysqld
	chkconfig --add mysqld && chkconfig mysqld on
	mv /etc/my.cnf{,_bk}
	wget -O /etc/my.cnf http://panel.ropon.top/panel/lnmp/config/my.txt
	sed -i "s@/usr/local/mysql@${MysqlDirs[MysqlInstallDir]}@" /etc/my.cnf
	sed -i "s@/home/mysql@${MysqlDirs[MysqlDataDir]}@" /etc/my.cnf
	
	[ "${MysqlVer}" == "5.5.62" ] &&  { temp="#explicit_defaults_for_timestamp" ; sed -i "s@explicit_defaults_for_timestamp@$temp@" /etc/my.cnf; }
	[ "${MysqlVer}" == "5.7.25" ] && MysqlInstallsSripts="${MysqlDirs[MysqlInstallDir]}/bin/mysqld --initialize-insecure" || MysqlInstallsSripts="${MysqlDirs[MysqlInstallDir]}/scripts/mysql_install_db"
	#因mysql初始化命令不同，判断mysql版本是否5.7
	$MysqlInstallsSripts --user=$RunUser --basedir=${MysqlDirs[MysqlInstallDir]} --datadir=${MysqlDirs[MysqlDataDir]} #初始化mysql数据
	chown $RunUser.$RunUser -R ${MysqlDirs[MysqlDataDir]}
	service mysqld start
	
	# 判断加path
	[ -z "`grep ^'export PATH=' /etc/profile`" ] && echo "export PATH=${MysqlDirs[MysqlInstallDir]}/bin:\$PATH" >> /etc/profile
	[ -n "`grep ^'export PATH=' /etc/profile`" -a -z "`grep ${MysqlDirs[MysqlInstallDir]} /etc/profile`" ] && sed -i "s@^export PATH=\(.*\)@export PATH=${MysqlDirs[MysqlInstallDir]}/bin:\1@" /etc/profile
	sleep 1
	. /etc/profile
	
	${MysqlDirs[MysqlInstallDir]}/bin/mysql -e "grant all privileges on *.* to root@'127.0.0.1' identified by \"${RootPassword}\" with grant option;" #修改root密码
	${MysqlDirs[MysqlInstallDir]}/bin/mysql -e "grant all privileges on *.* to root@'localhost' identified by \"${RootPassword}\" with grant option;" #修改root密码
	${MysqlDirs[MysqlInstallDir]}/bin/mysql -uroot -p${RootPassword} -e "delete from mysql.user where Password='';" #清理空密码
	${MysqlDirs[MysqlInstallDir]}/bin/mysql -uroot -p${RootPassword} -e "delete from mysql.db where User='';" #清理空账号
	${MysqlDirs[MysqlInstallDir]}/bin/mysql -uroot -p${RootPassword} -e "delete from mysql.proxies_priv where Host!='localhost';" #清理非本地用户权限
	${MysqlDirs[MysqlInstallDir]}/bin/mysql -uroot -p${RootPassword} -e "drop database test;" #删除test数据库
	${MysqlDirs[MysqlInstallDir]}/bin/mysql -uroot -p${RootPassword} -e "reset master;" #清理所有二进制日志并重新生成
	
	rm -rf /etc/ld.so.conf.d/{mysql,mariadb,percona,alisql}*.conf
	[ -e "${MysqlDirs[MysqlInstallDir]}/my.cnf" ] && rm -rf ${MysqlDirs[MysqlInstallDir]}/my.cnf
	echo "${MysqlDirs[MysqlInstallDir]}/lib" > /etc/ld.so.conf.d/mysql.conf #初始化mysql动态函数库
	ldconfig #刷新动态函数库
	Echo "msg" "Mysql${MysqlFlag}的root密码是: ${RootPassword},保存到mysql${MysqlFlag}_password.txt文件中"
	echo Mysql${MysqlFlag}的root密码是: ${RootPassword} > /root/mysql${MysqlFlag}_password.txt
	source ${PanelDirs[PanelInstallDir]}/.py3env/bin/activate && python  ${PanelDirs[PanelInstallDir]}/manager.py rerootpwd -r ${RootPassword}
	deactivate
	service mysqld restart
	popd
}

Mysql() {
	if [ -z $MysqlVer ]; then
		Echo "msg" "跳过安装Mysql"
	else
		Echo "msg" "正在安装Mysql"
		yum install -y gcc-c++ perl ncurses ncurses-devel libaio numactl numactl-libs perl-Module-Install.noarch
		InstallMysql
	fi
}
