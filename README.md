# udtPushToCMDB
解析udt的库文件并推送给CMDB

##（此项目已经停止维护，被新版vservermap中的Restful接口代替）



# 简介
本程序主要作用是把udt产生的allarpmacfile解读成 mac,ip,设备sn，接口 的四元组。通过API接口推送到cmdb的数据库中。



# 程序运行过程设计
1. 取udt文件夹中allarpmacfile的最后一行的id，然后创建多线程，grep 每一个arp信息行，然后进行该id的mac信息处理。 最终处理的结果是返回精确的 ip mac 接口 设备的SN号   四元组信息。
2. 程序开始要对allarpmacfile 是否存在，api接口是否正常可用做一次判断。程序执行过程中，插入四元组动作要有日志记录。 api调用失败要有日志记录。
3. 取值策略，只需独立id的第一行和最后一行，所以请确保udt结果中最后一行是直连服务器的交换机接口， 实现的方法是，udt中配置文件应该吧核心放在前边。 如果一个独立id对应的只有一行记录（说明没有二层信息），则返回‘unknow1’，并且记录在日志文件中体现为‘no interface info’。   若返回的大于一条记录，那么第一条记录毋庸置疑肯定是arp信息，直接处理字符串取出ip和mac备用，第二条记录需要过滤判断（发现Bridge.Agg 字符串,返回unknow2），没有被过滤掉的信息被认为是有效的二层mac-interface信息（ip-mac-device-if）
4. 寻找物理交换机的sn号，过程为：通过第三部中判断得到的有效的mac信息行中的交换机ip和接口信息组合成ipif字符串，即 192.168.254.3-2   之类的字符串。 用这个字符串对 ini配置文件过滤， 一定会得到一个sn号。 这个sn号就确定了一个物理交换机。 
5. 配置文件的含义：第一个字段ipif ，即管理ip和slot号，作用是标示同一个管理ip下不同的交换机（IRF结构），如果是非IRF结构的交换机，这个字段填写ip-1即可，例如DB2交换机就不是irf结构。这个配置文件的作用主要是，可以让程序通过udt-allarpmac.html 中的二层信息找到这个二层交换机的SN号。



# 注意事项
注意：unknow1 的意思只只有三层信息的条目；unknow2 的意思是 有二层条目但是是汇聚口，所以被过滤掉了。 sn error的意思是寻找sn号的时候有问题。
注意；10.2.8.1 如果有完整的id信息也会被写入数据库
注意：数据会有重复的原因是，一个ip的三层信息可能会出现在多台交换机上。 但是这并不影响结果，不管出现多少条三层信息，设备真实链接的交换机的端口总是固定的。 我这个层面无法去重复，所以在插入对方数据库的时候请自动加ID。
注意：当增加网络设备时,需要在配置文件中添加sn条目,否则会在日志中出现find sn error 错误。
注意：当日志中出现大量 find sn error，说明程序在便利allarpmac库文件的时候，出现有条目（ip+solt号）无法再ini文件中找到序列号。考虑是否出现了新增设备。



接口验证成功：

[root@localhost udt_pushto_API]# python udt_pushto_api.py 
Data={infoList:[{'switch_port': '31', 'switch_sn': '324', 'server_ip': '192.168.2.1', 'switch_port_mac': 'null', 'server_sn': 'null', 'server_network_mac': '00:22:19:ad:a6:e9'}]}
{"result":"0","msg":"更新入库成功"}{"status":0,"message":"OK","data":{}}

--------------------------------------
bug1修复：
udt程序已经出现了一个严重的阻碍， CLI方式需要两次才能获取到完整的arp信息， 这样对线上设备有侵入性，更糟糕的是mac信息无法通过这种方式获取完整的。也就是说肯定有mac信息被遗漏了。
也就是说，肯定会有一些设备有三层信息但是找不到二层信息。  这种CLI方式获取已经遇到了瓶颈， 本次bug修复仅仅是临时解决arp表的完整问题， 至少先保证ip表是全的。个别服务器找不到接口的bug不会在这里实现了。  下一步准备用go语言读取snmp的方式进行全盘完善。


## 开发环境
python 2.7.5

## 作者介绍
yihongfei  QQ:413999317   MAIL:yihf@liepin.com

CCIE 38649


## 寄语
为网络自动化运维尽绵薄之力
