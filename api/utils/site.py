#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/7/1 12:43
# @Author  : Ropon
# @File    : site.py

import os
from api.utils.tools import execShell


class PanelSite(object):
    def __init__(self, webserver="nginx", vhostpath="/home/panel/vhost", sslpath="/home/panel/ssl",
                 repath="/home/panel/rewrite", panelpath="/home/panel/newpanel", nginxpath="/usr/local/nginx"):
        self._webserver = webserver
        self._vhostpath = vhostpath
        self._sslpath = sslpath
        self._repath = repath
        self._panelpath = panelpath
        self._nginxpath = nginxpath

    def check(self):
        if not os.path.exists(self._nginxpath):
            return "还没安装nginx服务,请先安装"
        if int(execShell("ps aux|grep nginx|grep -v grep|wc -l")) == 0:
            return "还没启动nginx服务,请先启动"
        self.checkpathisexists(self._vhostpath)
        self.checkpathisexists(self._sslpath)
        self.checkpathisexists(self._repath)
        self.checkpathisexists(self._panelpath)

    def checkpathisexists(self, path):
        if not os.path.exists(path):
            execShell(f"mkdir -p {path}")
            execShell(f"chown -R www.www {path}")
            execShell(f"chmod -R 744 {path}")

    def save(self, filename, content, mode="w"):
        try:
            fp = open(filename, mode)
            fp.write(content)
            fp.close()
            return True
        except:
            return False

    def checknginx(self):
        res = execShell("/usr/local/nginx/sbin/nginx -t -c /usr/local/nginx/conf/nginx.conf")
        successflag = "successful"
        if res.find(successflag) == -1:
            return "nginx有语法错误，请排除后重新创建站点。"
        return "ok"

    def reloadnginx(self):
        return execShell("/usr/local/nginx/sbin/nginx -s reload")

    def copyindexand404(self, root_path):
        if not os.path.isfile(f"{root_path}/index.html"):
            execShell(f"/usr/bin/cp {self._panelpath}/data/index.html {root_path}")
        if not os.path.isfile(f"{root_path}/404.html"):
            execShell(f"/usr/bin/cp {self._panelpath}/data/404.html {root_path}")

    def create_site(self, site_name=None, bind_domain=None, root_path=None, domain_301="", is_ssl=False, is_log=False,
                    log_path=None, default_index=None,
                    php_ver=None, extra_kwargs={}):
        res = execShell(f"file /dev/shm/{php_ver}-cgi.sock")
        successflag = "socket"
        if res.find(successflag) == -1:
            return f"{php_ver}还没安装或没启动"
        if self._webserver == "nginx":
            ssl_conf = '''
    #配置ssl
    listen 443 ssl http2;
	listen [::]:443 ssl http2;
	ssl_certificate /home/panel/ssl/%s.crt;
	ssl_certificate_key /home/panel/ssl/%s.key;
	ssl_session_timeout 1d;
	ssl_session_cache shared:SSL:50m;
	ssl_session_tickets off;
	ssl_protocols TLSv1.1 TLSv1.2 TLSv1.3;
	ssl_ciphers "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-SHA256:AES128-SHA256:AES256-SHA:AES128-SHA:DES-CBC3-SHA:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!MD5:!PSK:!RC4";
	ssl_prefer_server_ciphers on;
	add_header Strict-Transport-Security max-age=15768000;
	ssl_stapling on;
	ssl_stapling_verify on;
''' % (site_name, site_name)
            denyua_conf = '''
    #屏蔽非常见UA
	if ($http_user_agent ~* "Scrapy|HttpClient|YandexBot|iFeedDemon|JikeSpider|Indy Library|Alexa Toolbar|AskTbFXTV|AhrefsBot|CrawlDaddy|CoolpadWebkit|Java|Feedly|UniversalFeedParser|ApacheBench|Microsoft URL Control|Swiftbot|ZmEu|oBot|jaunty|Python-urllib|lightDeckReports Bot|YYSpider|DigExt|YisouSpider|HttpClient|MJ12bot|heritrix|EasouSpider|LinkpadBot|Ezooms|^$") {
	    return 403;
    }'''
            referer_conf = '''
    #配置防盗链
	location ~ .*\.(wma|wmv|asf|mp3|mmf|jpg|gif|png|swf|flv|mp4)$ {
	    valid_referers none blocked %s *.baidu.com *.baiducontent.com;
	    if ($invalid_referer) {
		    return 403;
	    }
    }''' % bind_domain
            safe_conf = '''
    #配置请求方式，根据实际情况调整
	if ($request_method !~ ^(GET|HEAD|OPTIONS|POST|PUT|DELETE)$) {
	    return 403;
    }
    #根目录下压缩包禁止下载
	location ~ \.(zip|rar|sql|tar.gz|7z)$ {
	    return 403;
    }'''
            cache_conf = '''
    #图片视频静态文件缓存30天
	location ~ .*\.(gif|jpg|jpeg|png|bmp|swf|flv|mp4|ico)$ {
	    expires 30d;
	    access_log off;
    }
    #js/css静态文件缓存7天
    location ~ .*\.(js|css)?$ {
	    expires 7d;
	    access_log off;
    }'''
            log_conf = '''
    #日志配置
    access_log %s_access.log;
	error_log %s_error.log;''' % (log_path, log_path)
            set_404_conf = '''
    #配置404错误页
	error_page 500 502 404 /404.html;'''
            ssl_301_conf = '''
    #配置https跳转
	if ($ssl_protocol = "") { return 301 https://$server_name$request_uri; }'''
            if not is_ssl:
                ssl_301_conf = ""
            set_301_conf = '''
    #配置301跳转
	if ($host !~* %s) { 
		rewrite ^/(.*)$ http://%s/$1 permanent; 
	}
	%s
    ''' % (domain_301, domain_301, ssl_301_conf)
            if not is_ssl:
                ssl_conf = ""
            if not extra_kwargs.get('deny_ua'):
                denyua_conf = ""
            if not extra_kwargs.get('deny_referer'):
                referer_conf = ""
            if not extra_kwargs.get('safe'):
                safe_conf = ""
            if not extra_kwargs.get('cache'):
                cache_conf = ""
            if not extra_kwargs.get('set_404'):
                set_404_conf = ""
            if not extra_kwargs.get('set_301'):
                set_301_conf = ""
            if not is_log:
                log_conf = ""
            nginx_conf = '''
server {
	listen 80;
	listen [::]:80;
	%s
	server_name %s;
	root %s;
	index %s;
	%s
    %s
    %s
    %s
	%s
	location ~ [^/]\.php(/|$) {
		fastcgi_pass unix:/dev/shm/%s-cgi.sock;
		#/dev/shm这个目录是linux下一个利用内存虚拟出来的一个目录
		fastcgi_index index.php;
		include fastcgi.conf;
	}
	%s
	location ~ /\.ht {
		deny all;
	}
	%s
}''' % (ssl_conf, bind_domain, root_path, default_index, set_301_conf, denyua_conf, referer_conf, safe_conf,
        set_404_conf, php_ver, cache_conf, log_conf)
            filename = f"{self._vhostpath}/{site_name}.conf"
            if self.save(filename, nginx_conf):
                self.checkpathisexists(root_path)
                res = self.checknginx()
                if res == "ok":
                    self.copyindexand404(root_path)
                    self.reloadnginx()
                else:
                    os.remove(filename)
                    return res

    def delete_site(self, site_name=None, root_path=None, is_ssl=False, log_path=""):
        filename = f"{self._vhostpath}/{site_name}.conf"
        if os.path.isfile(filename):
            os.remove(filename)
            if os.path.exists(root_path):
                # pass
                # 删除网站根目录
                execShell(f"/usr/bin/rm -rf {root_path}")
                # 删除证书文件
                if is_ssl:
                    execShell(f"/usr/bin/rm -rf {self._sslpath}/{site_name}.crt")
                    execShell(f"/usr/bin/rm -rf {self._sslpath}/{site_name}.key")
                if log_path:
                    execShell(f"/usr/bin/rm -rf {log_path}_access.log")
                    execShell(f"/usr/bin/rm -rf {log_path}_error.log")
            self.reloadnginx()

    def update_site(self):
        pass
