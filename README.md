## 名称 
substitudeDDNS

## 简介
指定任意数量计算机，替代ddns+域名功能。

### 缘由
动态ip变更后，链接远程桌面都要重新输ip、用户名、密码，并确认链接。很不方便。DDNS+域名每年也要不少费用。
此软件可选任意域名本地配置，自动同步。仅需1个固定ip vps。


系统需求：1个固定IP充当server,
支持任意数量客户。
支持win  linux系统



## 软件配置
配置.py内config_data 字典，或配置同目录下config.json

behavior :     
Behavior.SERVER       服务器，需配置ServerIP，ServerPort ，首次启动若不存在自动创建并修改为本机外网ip。应用于固定IPvps。若多域名，则必须手动添加至config_data字典。

Behavior.CLIENT_UP    上传本机ip公网ip至Server，需配置change_domain_name 为本机ip对应域名


Behavior.CLIENT_GET   获取共享的hosts表并更新到本机



## 系统
win系统建议配置：
修改权限：c:\windows\System32\driver\etc\hosts 文件user组增加写入和修改权限

或启动方式选择管理员启动并每次点击确定。






## 自启动配置


### linux (已测试 树莓派4 debian11)
建议配置supervisor

配置方法示例

nano /etc/supervisor/conf.d/substituteDDNS.conf

[program:substituteDDNS]
directory = /home/pi/subDDNS
command=/usr/bin/python3.9 /home/用户名/subDDNS/substituteDDNS.py /home/用户名/subDDNS/config.json
autorestart=true
startsecs = 40        ; 
autorestart = true   ; 程序异常退出后自动重启
startretries = 30     ; 启动失败自动重试次数，默认是 3


redirect_stderr = false  ; 把 stderr 重定向到 stdout，默认 false
stdout_logfile_maxbytes = 50MB  ; stdout 日志文件大小，默认 50MB
stdout_logfile = /home/用户名/subDDNS/supervisor.log
stdout_logfile_backups= 5
loglevel=info
user=root
stderr_logfile_maxbytes = 50MB  ; stdout 日志文件大小，默认 50MB
stderr_logfile = /home/用户名/subDDNS/supervisorerr.log
stderr_logfile_backups= 5



### win 

启动文件夹内
增加
substituteDDNS.bat

修改内容为
start cmd /k "cd /d "D:\所在目录\" && python.exe substituteDDNS.py "
