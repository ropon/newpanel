#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top


InstallPanel() {
	pushd $BaseDir
	# 批量下载并解压所需包
	for key in ${!PanelFiles[*]}; do
		[ ! -f ${PanelFiles[$key]}.tar.gz ] && Download ${MirrorLink}/${PanelFiles[$key]}.tar.gz
		[ ! -d ${PanelFiles[$key]} ] && tar xzf ${PanelFiles[$key]}.tar.gz
    done
	# 批量检测并创建所需目录
	for key in ${!PanelDirs[*]}; do
		[ ! -d "${PanelDirs[$key]}" ] && mkdir -p ${PanelDirs[$key]}
    done
	pushd ${PanelFiles[python]}
	# --enable-optimizations 优化python 但安装较慢
	#./configure --prefix=/usr/local/python3.6.8 --enable-optimizations
	./configure --prefix=${PanelDirs[PythonInstallDir]} --enable-optimizations
	make -j${Thread} && make install
	ln -sf ${PanelDirs[PythonInstallDir]}/bin/python3.6 /usr/bin/python3
	ln -sf ${PanelDirs[PythonInstallDir]}/bin/pip3.6 /usr/bin/pip3
	mkdir -p ~/.pip
	cat > ~/.pip/pip.conf <<EOF
[global] 
trusted-host=mirrors.aliyun.com 
index-url=http://mirrors.aliyun.com/pypi/simple/
EOF
	popd
	/usr/bin/mv ${PanelFiles[panel]}/* ${PanelDirs[PanelInstallDir]}
	pip3 install virtualenv
	${PanelDirs[PythonInstallDir]}/bin/virtualenv --python=/usr/bin/python3 ${PanelDirs[PanelInstallDir]}/.py3env
	source ${PanelDirs[PanelInstallDir]}/.py3env/bin/activate && pip3 install -r ${PanelDirs[PanelInstallDir]}/requirements.txt
	deactivate
	cat > /etc/systemd/system/newpanel.service <<EOF
[Unit]
    Description=Panel Service Start
[Service]
    BASE=${PanelDirs[PanelInstallDir]}
    ENV=$BASE/.py3env/bin/activate
    ExecStart=/usr/bin/bash -c "source ${PanelDirs[PanelInstallDir]}/.py3env/bin/activate; uwsgi --ini ${PanelDirs[PanelInstallDir]}/uwsgi.ini"
    ExecReload=/usr/bin/bash -c "source ${PanelDirs[PanelInstallDir]}/.py3env/bin/activate; uwsgi --reload ${PanelDirs[PanelInstallDir]}/uwsgi.pid"
    ExecStop=/usr/bin/bash -c "source ${PanelDirs[PanelInstallDir]}/.py3env/bin/activate; uwsgi --stop ${PanelDirs[PanelInstallDir]}/uwsgi.pid"
[Install]
    WantedBy=multi-user.target
EOF
	if [ -d "${PanelDirs[PanelInstallDir]}/.py3env" ]; then
		for key in ${!PanelFiles[*]};do
			rm -rf ${PanelFiles[$key]}.tar.gz ${PanelFiles[$key]}
		done
	fi
	popd
	systemctl enable newpanel
	systemctl start newpanel
	CURL=$(which curl)
	wanip=$($CURL -s ip.idiyrom.com?type=ip)
	echo "http://${wanip}:8088"
	source ${PanelDirs[PanelInstallDir]}/.py3env/bin/activate && python  ${PanelDirs[PanelInstallDir]}/manager.py repasswd
	deactivate
	echo "systemctl start|stop|restart|reload newpanel"
}

Panel() {
	if [ -z $PanelVer ]; then
		Echo "msg" "跳过安装Panel"
	else
		Echo "msg" "正在安装Panel${PanelVer}"
		yum install gcc-c++ openssl-devel bzip2-devel expat-devel gdbm-devel readline-devel sqlite-devel -y
		InstallPanel
	fi	
}
