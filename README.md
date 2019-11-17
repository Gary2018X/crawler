# crawler
大学学术交流信息爬虫程序  
1.handle_error.py   
操作步骤：  
      A.安装依赖的库：requests#获取网页内容 pymysql#数据库操作 chardet#获取网页编码 urllib.request#打开网页  
      B.连接自己的数据库：代码第14行（database函数中）conn = pymysql.connect(host='127.0.0.1', user='username', password='password',          db='database_name',charset='utf8')  # 连接数据库,username,password,database_name对应自己的数据库信息。  
      C.运行主程序
