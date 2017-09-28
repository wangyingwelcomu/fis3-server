# fis-server

## 说明

目录结构
```
fis3server/
├── fis-conf.js --fis3 Client configure
├── receiver.php --fis3 Servier script
├── HTTPServerWithUpload.py --fis3 python Servier script

```

## fis3监听模式 webServer上传文件配置修改
默认最大文件为100M
### nginx.conf
场景一:
``` bash
http {
    #---
    client_max_body_size 100m;
    #---
}
```

场景二:反向代理
``` bash
http {
    #-默认-
    client_max_body_size 10m;
    #---
    include vhost/*.conf;
}
#80.conf
server {
    listen 80;
    server_name you.domain.com;
    root /home/www/htdocs;
    index index.php index.html index.htm;
    
    #---
    #反向代理 fis3server
    location ^~ /fis3server {
        #代理转发POST上传大小
        client_max_body_size  100m;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_pass http://127.0.0.1:8001;
    }
    #---
}
#8001.conf
server {
    listen 8001;
    server_name you.domain.com;
    root /home/www/htdocs;
    index index.php index.html index.htm;
    #---
    location ~ \.php$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        #代理转发过来的数据,POST上传文件大小限制
        client_max_body_size  100m;
    }
    #---
}

```


### php.ini
``` bash
http {
    #增大脚本执行时间，防止文件上传速度慢时上传超时报错
    max_execution_time = 600;
    max_input_time = 600;
    #每个PHP页面所吃掉的最大内存
    memory_limit = 100m;
    # 打开文件上传
    file_uploads = on;
    #upload tmp dir
    upload_tmp_dir = /tmp;
    #允许上传文件大小的最大值
    upload_max_filesize = 100m;
    #表单POST给PHP的所能接收的最大值
    post_max_size = 100m;
    #---
}
```
> 一般来说：memory_limit > post_max_size > upload_max_filesize 

### php-fpm.conf
``` html
<value name="rlimit_files">65535</value>
<value name="request_terminate_timeout">0s</value>
``````