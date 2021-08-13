#简介
=====
happyPerf是基于python-locust库搭建的性能测试平台，多线程（协程）对目标对象进行压测

#我能做什么
=====
1、通过提供的模板，自动生成压测用例脚本（生成后需根据请求body进行修改参数化）

2、通过配置文件，自定义压测请求参数化，压测数据和测试脚本的分离

3、支持多线程的并发压测，长时间的稳定性压测

4、支持分布式的多客户端进行压测

5、集成到prometheus+grafana，可视化监控压测主机资源指标

#框架介绍
=====

##python版本：
python3.6+，locust1.3+

##/api（coding中）
封装请求方法

接口mock

##common
公共方法和函数

##config
yaml配置文件，通过配置文件自定义压测脚本相关参数化

##reqdatas
yaml配置文件中的reqjson文件，内容接口请求body样例

##testcase
压测脚本，通过读取config配置文件以及reqdatas文件请求body并进行自定义参数化

##logs
压测脚本运行输出日志文件

#安装和使用
=====
##安装相关库
pip install -r requirements.txt

##使用
1、配置config/env.ini文件，配置app和pc的接口host地址

2、在config/configlocust.yaml中配置需要压测的接口相关参数

###格式内容eg：根据压测接口所需参数化自定义


和压测脚本方法名称一致，必填
- apporderlocust:

  测试环境test、uat，必填
  - env: 'test'
  
  要模拟的渠道，压测的是C端就填写app，压测的是pc端就填写pc，必填
  - channel: 'app'
  
  接口后缀地址，必填
  - apiurl: 'hall/order/generateOrder'
  
  请求body,请求报文样例文件路径，必填
  - reqfile: 'F:\pyproject\pxx\reqdatas\apporderlocust.json'
  
  是否循环取数，true循环取数，如果为false，当参数用户数取完后结束压测，必填
  - iscircle: 'false'
  
  是否并发，如果为true，所有用户到达集合点，同时发起请求，false则不并发，必填
  - isbf: 'true'
  
  压测用户总数，限单个用户循环取数压测使用，需大于等于locust-web设置的’Number of total users to simulate‘，非必填（默认值100）
  - yctotals: 100
  
  参数化数据保存的excel文件，通过读取excel获取参数化数据，如果不需要就不必填写
  - datas: 'F:\pyproject\happyPerf\datas\usecoupon.xlsx'
  
  登陆mobiles参数化数据，必须是已完善学生信息的用户，以便获取studentid
  - telno:
    - '13921360104'
    - '13921360105'
    - '13921360101'
    - '13921360106'
    - '18565667162'
  
  
  3、配置好后，运行/common/autogenerate_py,python autogenerate_py.py,输入上述配置文件中的压测脚本方法名称（eg：apporderlocust），自动生成压测脚本
  
  4、生成的压测脚本（eg：apporderlocust.py）在testcase目录下，自定义对脚本中的压测数据进行参数化修改
  
    ps：测试用例脚本中继承TaskSet的类，请求参数reqparams['参数名']进行自定义修改
  
  5、运行locust命令：
  作为主机master：locust --web-host=0.0.0.0 --master -f {压测脚本名称}.py
  作为从机worker：locust --master-host={master-ip} --worker -f {压测脚本名称}.py
  
  locust命令自行度娘
  
  6、浏览器打开：http://localhost{master-ip}:8089
  测试地址：http://172.16.0.131:8089

  对目标压测主机监测
  ======
  目标机安装node-explore即可，后续补充安装操作说明
  测试地址：http://172.16.0.131:3000/?orgId=1，登陆：admin/123456
