#!/bin/bash
# Author: Ropon
# Blog: https://www.ropon.top
LANG=en_US.UTF-8
Mem=`free -m | awk '/Mem:/{print $2}'`
Swap=`free -m | awk '/Swap:/{print $2}'`

InitBase() {
	# 检查是否有wget命令
	which wget >/dev/null 2>&1
	[ $? -ne 0 ] && yum install -y wget
	# 调整yum源及epel源
	mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
	wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
	wget -O /etc/yum.repos.d/epel-7.repo http://mirrors.aliyun.com/repo/epel-7.repo
	yum clean all
	yum makecache
	# 安装常用命令
	yum install -y net-tools vim screen tcpdump ntp sysstat
	# 优化配置及参数
	# - 关闭禁用firewalld、NetworkManager服务、postfix服务
	systemctl disable firewalld
	systemctl stop firewalld
	systemctl disable NetworkManager
	systemctl stop NetworkManager
	systemctl disable postfix
	systemctl stop postfix
	
	#优化You have new mail in /var/spool/mail/root 提示
	echo "unset MAILCHECK" >> /etc/profile
	
	# - 关闭禁用SELINUX
	sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
	grep SELINUX=disabled /etc/selinux/config
	setenforce 0
	# 调整ssh端口为22000
	sed -i 's/#Port 22/Port 22000/'  /etc/ssh/sshd_config
	# 安装iptables服务
	yum install -y iptables-services
	cat > /etc/sysconfig/iptables <<EOF
*filter
# 配置几个链默认行为 比如INPUT链 默认丢弃 
# [0:0] 第一个值表示丢弃包的个数
# 第二个值表示丢弃包的总字节，其他同理。
:INPUT DROP [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:syn-flood - [0:0]
# 本地回环
-A INPUT -i lo -j ACCEPT

-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
# 放行SSH端口
-A INPUT -p tcp -m state --state NEW -m tcp --dport 22000 -j ACCEPT
# 放行web http端口
-A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
# 放行web https端口
-A INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
# 放行FTP端口
-A INPUT -p tcp -m state --state NEW -m tcp --dport 21 -j ACCEPT
# 放行FTP被动端口
-A INPUT -p tcp -m state --state NEW -m tcp --dport 20000:30000 -j ACCEPT
# 放行mysql端口
-A INPUT -p tcp -m state --state NEW -m tcp --dport 3306 -j ACCEPT
# 放行panel端口
-A INPUT -p tcp -m state --state NEW -m tcp --dport 8088 -j ACCEPT

# ICMP包控制
-A INPUT -p icmp -m limit --limit 1/sec --limit-burst 10 -j ACCEPT
-A INPUT -f -m limit --limit 100/sec --limit-burst 100 -j ACCEPT

# DDOS防护
-A INPUT -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -j syn-flood
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A syn-flood -p tcp -m limit --limit 3/sec --limit-burst 6 -j RETURN
-A syn-flood -j REJECT --reject-with icmp-port-unreachable

# UDP控制
-A OUTPUT -d 119.29.29.29/32 -p udp -m udp --dport 53 -j ACCEPT
-A OUTPUT -d 114.114.114.114/32 -p udp -m udp --dport 53 -j ACCEPT
-A OUTPUT -p udp -m udp --dport 123 -j ACCEPT
-A OUTPUT -p udp -j DROP
COMMIT
EOF
	service iptables reload
	# 调整DNS配置
	cat > /etc/resolv.conf <<EOF
nameserver 119.29.29.29
nameserver 114.114.114.114
EOF

	# 调整时区
	rm -rf /etc/localtime
	ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

	# 同步时间
	sed -i '/ntpdate/d' /var/spool/cron/root
	echo '*/10 * * * * /usr/sbin/ntpdate cn.pool.ntp.org ' >>/var/spool/cron/root
	service crond restart
	ntpdate -u cn.pool.ntp.org
	
	# 优化历史命令history
	[ -z "$(grep ^'export PROMPT_COMMAND=' /etc/bashrc)" ] && cat >> /etc/bashrc << EOF
export PROMPT_COMMAND='{ msg=\$(history 1 | { read x y; echo \$y; });logger "[euid=\$(whoami)]":\$(who am i):[\`pwd\`]"\$msg"; }'
EOF
	# 优化SSH配置
	# - 关闭SSH反向查询，以加快SSH的访问速度
	sed -i 's@.*UseDNS yes@UseDNS no@' /etc/ssh/sshd_config
	# - 禁止空密码登录
	sed -i 's@PermitEmptyPasswords no@PermitEmptyPasswords no@' /etc/ssh/sshd_config
	
	# 内核参数优化
	# - 表示套接字由本端要求关闭，这个参数决定了它保持在FIN-wAIT-2状态的时间，默认值是60秒，建议调整为2
	echo 'net.ipv4.tcp_fin_timeout = 2' >> /etc/sysctl.conf
	# -表示开启重用，允许TIME-wAIT sockets重新用于新的TCP链接，默认值为0，表示关闭
	echo 'net.ipv4.tcp_tw_reuse = 1' >> /etc/sysctl.conf
	# - 表示开启TCP链接中TIME_WAIT sockets的快速回收 默认为0 表示关闭，不建议开启，因为nat网络问题
	echo 'net.ipv4.tcp_tw_recycle = 0' >> /etc/sysctl.conf

	# - 表示开启SYN Cookies功能，当出现SYN等待队列溢出时，启用Cookies来处理，可防范少量SYN攻击
	echo 'net.ipv4.tcp_syncookies = 1' >> /etc/sysctl.conf
	# - 表示当keepalive启用时，TCP发送keepalive消息的频度，默认是2小时，建议更改为10分钟
	echo 'net.ipv4.tcp_keepalive_time =600' >> /etc/sysctl.conf
	# - 该选项用来设定允许系统打开的端口范围，即用于向外链接的端口范围
	echo 'net.ipv4.ip_local_port_range = 32768   60999' >> /etc/sysctl.conf
	# - 表示SYN队列的长度 默认为1024 建议加大队列的长度，为8182或更多
	#   这样可以容纳更多等待链接的网络连接数，该参数为服务器端用于记录那些尚未收到客户端确认信息的链接请求的最大值
	echo 'net.ipv4.tcp_max_syn_backlog = 8182' >> /etc/sysctl.conf
	# - 该选项默认值是128，这个参数用于调节系统同时发起的TCP连接数，在高并发的请求中，默认的值可能会导致链接超时或重传，因此，需要结合并发请求数来调节此值
	echo 'net.core.somaxconn = 1024' >> /etc/sysctl.conf
	# - 表示系统同时保持TIME_WAIT套接字的最大数量，如果超过这个数值，TIME_WAIT套接字将立刻被清除并打印警告信息，默认为5000
	#   对于Aapache，Nginx等服务器来说可以将其调低一点，如改为5000-30000，不用业务的服务器也可以给大一点，比如LVS，Squid
	echo 'net.ipv4.tcp_max_tw_buckets = 5000' >> /etc/sysctl.conf
	# - 表示内核放弃建立链接之前发送SYN包的数量 默认是6
	echo 'net.ipv4.tcp_syn_retries = 1' >> /etc/sysctl.conf
	# - 参数的值决定了内核放弃链接之前发送SYN+ACK包的数量 默认是2
	echo 'net.ipv4.tcp_synack_retries = 1' >> /etc/sysctl.conf
	# - 表示当每个网络接口接收数据包的速率比内核处理这些包的速率快时，允许发送到队列的数据包最大数 默认值为1000
	echo 'net.core.netdev_max_backlog = 1000' >> /etc/sysctl.conf
	# - 用于设定系统中最多有多少个TCP套接字不被关联到任何一个用户文件句柄上，如果超过这个数值，孤立链接将立即被复位并打印出警号信息
	#   这个限制只是为了防止简单的DoS攻击，不能过分依靠这个限制甚至人为减小这个值，更多的情况是增加这个值，默认是4096，建议该值修改为2000
	echo 'net.ipv4.tcp_max_orphans = 2000' >> /etc/sysctl.conf

	# - 以下参数是对iptables防火墙的优化
	# CentOS7.X系统中的模块名不是ip_conntrack，而是nf_conntrack
	echo
	'net.ipv4.nf_conntrack_max = 25000000
	net.ipv4.netfilter.nf_conntrack_max = 25000000
	net.ipv4.netfilter.nf_conntrack_tcp_timeout_established = 180
	net.ipv4.netfilter.nf_conntrack_tcp_timeout_time_wait = 120
	net.ipv4.netfilter.nf_conntrack_tcp_timeout_close_wait = 60
	net.ipv4.netfilter.nf_conntrack_tcp_timeout_fin_wait = 120' >> /etc/sysctl.conf

	sysctl –p

	# - 优化文件描述符
	echo '  *  -  nofile   100000  '  >>/etc/security/limits.conf
	
	# 更新系统
	yum update -y
}

#添加交换分区
Makeswapfile() 
{
	COUNT=$1
	dd if=/dev/zero of=/home/swapfile count=$COUNT bs=1M
	mkswap /home/swapfile
	swapon /home/swapfile
	chmod 600 /home/swapfile
	[ -z "`grep swapfile /etc/fstab`" ] && echo '/home/swapfile    swap    swap    defaults    0 0' >> /etc/fstab
}

Centos7() {
	Echo "msg" "正在优化系统"
	if [ "$Swap" == '0' ]; then
		if [ $Mem -le 1024 ]; then
			Echo "msg" "正在添加1G交换分区"
			Makeswapfile 1024
		elif [ $Mem -gt 1024 -a $Mem -le 2048 ]; then
			Echo "msg" "正在添加2G交换分区"
			Makeswapfile 2048
		fi
	fi
	InitBase
	[ $? -eq 0 ] && Echo "success" "系统优化成功"
	echo "centos7 init success" > /root/.InitCentos.log
}
