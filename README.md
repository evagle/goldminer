Goldminer system

Step1. Pull docker image

```

$docker pull registry.cn-hangzhou.aliyuncs.com/evagle/goldminer

```
Step2. Start docker container and mount code repo

```
$docker run -it -d -v /path/to/goldminer:/opt/goldminer:rw --name goldminer goldminer
$docker exec -it goldminer /bin/bash
$cd /opt/goldminer && python setup.py install
```