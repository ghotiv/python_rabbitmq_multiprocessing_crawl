# python_rabbitmq_multiprocessing_crawl
use python,rabbitmq,multiprocessing,casperjs for crawling<br/>

程序主要用来获取国际快递物流信息,<br/>
用到技术：rabbitmq,casperjs,multiprocessing<br/>
解决问题：<br/>
	1.分布式爬虫<br/>
	2.casperjs可以模拟浏览器获取数据,解决js加载数据,普通模块request获取不到的问题<br/>
	3.multiprocessing可以利用多核<br/>
	
最初是利用xmlrpc读取和写入数据到openerp（数据库,postgresql）<br/>
为方便查看,修改了,这里用txt和excel<br/>

安装：<br/>
	#install casperjs test on ubuntu 14.04
	#casperjs 1.1.0 phantomjs 1.9.0
	sudo apt-eget install phantomjs 
	$ git clone git://github.com/n1k0/casperjs.git
	$ cd casperjs
	$ ln -sf `pwd`/bin/casperjs /usr/local/bin/casperjs
	sudo pip install xlrd,xlwt
	sudo apt-get install rabbitmq-server

使用：<br/>
	1.python receive_data.py  为rabbitmq消费者,用来接受和处理数据
	2.python send_data.py  读取快递单,运输商等信息列表; 
	3.python save_to_excel.py 读取success_data_***.txt的有效数据保存在excel,track_result.xls

程序说明：<br/>
	receive_data.py  ： 为rabbitmq消费者,用来接受和处理数据，可以部署多台机器
	send_data.py       ： 读取快递单,运输商等信息列表
	save_to_excel.py ： 读取success_data_***.txt的有效数据保存在excel,track_result.xls
	my_rabbitmq.py  ： rabbitmq 主函数，收发数据
	do_track.py            :   使用requests和casperjs获取,然后解析数据,调用multiprocessing
	track_data.py       ： 常用变量，读写excel
	my_process_pool.py :  记录multiprocessing异常日志
	read_excel.py       ： 读写excel
	track.js                     :  capsperjs调用函数
	rpc_api.py              ：xmlrpc对接openerp的api
	ftp_up.py                 :  将获取的json数据文件上传到php服务器
	test_excel.py          :   读取保存excel文件测试
	some_code.py       :    写过的一些函数片段
	

文档说明：<br/>
	sample_import.xls      为测试源数据
	error_data_***.txt      为出错数据
	success_data_***.txt  为获取成功数据
	track_***.log                处理数据日志

要做的：<br/>
	程序可以部署到网站上，导入快递基本信息excel后，输出快递详细信息的excel
