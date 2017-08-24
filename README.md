# Auth
## 状态 ：
###  当前状态 ：开发完成 
### 分支 ： 
  1. 主分支 ：master 
  
  2. 开发分支 ：dev-branch 
## 部署 ：
### 1. Docker 相关 （ 初次部署） 
### 2. 编写Auth.env : 
加入环境变量 ： 
```
  AUTH_SQL=mysql://<username>:<password>@<url-to-rds>/<database-name>
``` 
### 3.拉取镜像 
### 4.初始化数据库，迁移数据库 
