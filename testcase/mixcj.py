#coding='utf-8'
from gevent import monkey
monkey.patch_all()
import sys,os
sys.path.append(os.pardir)
#os.path.abspath('../..')
from gevent._semaphore import Semaphore
from locust.contrib.fasthttp import FastHttpUser
import json,datetime
from locust import task, between,SequentialTaskSet,events,TaskSet
import os,requests,ssl
import queue,re
from threading import Lock
from common import loginapp, readconfig_ex,loginappthread,logger,readenv,readexcel
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#import sys
#sys.setrecursionlimit(5000)
ssl._create_default_https_context = ssl._create_unverified_context
#读取配置文件参数
readcfg= readconfig_ex.readconfig('mixcj')
circle=readcfg['allparams']['iscircle']
bf=readcfg['allparams']['isbf']
env=readcfg['allparams']['env']
reqparams=readcfg['reqjson']
apiurl=readcfg['allparams']['apiurl']
couponids=readcfg['allparams']['couponid']
classids=readcfg['allparams']['classid']
productid=readcfg['allparams']['productid']
orderid=readcfg['allparams']['orderid']
try:
    ycnums=readcfg['allparams']['yctotals']
except (IOError,ValueError,KeyError) as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print(repr(e),exc_value,'配置文件yaml中未找到，取默认值100')
    ycnums=100
    pass
channel=readcfg['allparams']['channel']
#判断配置文件参数化设置，读取excel文件获取参数化数据
if 'datas' in readcfg['allparams']:
    paramdatas = readexcel.readdatas('usecoupon')
    loginmobile=paramdatas['loginaccount']
else:
    loginmobile = readcfg['allparams']['telno']
    #startloginmobile = loginmobile[0]
    #endloginmobile = loginmobile[-1]
rdenv=readenv.readenv(channel)
# 判断压测环境test or uat
if env == 'test':
    host=rdenv[0]
elif env == 'uat':
    host=rdenv[1]
else:
    print('未读取到测试环境配置--test or uat')
    exit(0)
#初始化登陆获取信息
#多线程登陆
params = loginappthread.mythreads(loginmobile,host,channel)
#print(params)
#单线程登陆
#params = loginapp.loginapp().login(loginmobile)
logger = logger.LocustLogger()

#创建集合点，当locust实例产生完成时触发（即所有用户启动完毕）
all_locusts_spawned = Semaphore()
#all_locusts_spawned.acquire()
def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()
    logger.get_locust_Hook()
# 挂在到locust钩子函数（所有的Locust示例产生完成时触发）
events.spawning_complete.add_listener(on_hatch_complete)

#TaskSet，所有用户按task权重比例压测
class order(TaskSet):
#SequentialTaskSet，所有用户按task顺序压测，SequentialTaskSet是TaskSet子类，作用就是忽略权重，完全根据编写顺序来控制任务执行顺序，多用于事务压测
#class order(SequentialTaskSet):
    def on_start(self):
        print('-----star------')

        try:
            # get_nowait() 取不到数据直接崩溃；get() 取不到数据会一直等待
            # data = self.user.user_data_queue.get_nowait()  # 取值顺序
            self.quelen = self.user.user_data_queue.qsize()
            #print(self.quelen)
            self.data = self.user.user_data_queue.get_nowait()  # 取值顺序

        except queue.Empty:  # 取不到数据时或设置的压测数据总数大于队列实际大小,退出程序
            print('account data run out, test ended.')
            exit(0)

        # 获取购课车列表
        getcardlist_url = host + 'hall/courseCart/findCourseCartList'
        self.getcarddata = {
            "studentId": self.data['stus']
        }

        # 检查课程是否在购课车
        getcardreq = requests.post(url=getcardlist_url, data=json.dumps(self.getcarddata),
                                   headers=self.data['heads'],
                                   verify=False)
        getcardrsp = getcardreq.json()
        productId = re.findall(r"productId.*?,", str(getcardrsp))
        for prodid in productid:
            if getcardrsp['code'] == 200 and str(prodid) in str(productId):
                print('课程产品',prodid, '课程已在购课车，开始结算')
            else:
                # 添加购课车
                addcart_url = host + 'hall/courseCart/addAndEditCourseCart'
                self.carddata = {
                    "studentId": self.data['stus'],
                    "commodityId": prodid  # 班级课程productid
                    }
                cardreq = requests.post(url=addcart_url, data=json.dumps(self.carddata), headers=self.data['heads'],
                                            verify=False)
                cardrsp = cardreq.json()
                if cardrsp['code'] == 200:
                    print(self.data['stus'], '添加购课车成功，开始结算')
                    # return self.stuid, self.all_headers, self.mobile
                else:
                    print(self.data['stus'], '添加购课车失败', cardrsp)
                    # sys.exit()
    '''
    def statmentorder(self):
        statmentorder_url = host + 'hall/order/calCourseCart'
        statmentorder_data = {
            "studentId": self.data['stus'],
            "couponIds":couponids,
            "classId":self.data['classid']
        }
        requests.post(url=statmentorder_url, data=json.dumps(statmentorder_data), headers=self.data['heads'],
                      verify=False)
    '''
    @task(50)#权重，数字越大占比越高
    def suborder(self):
        #lock = Lock()
        #lock.acquire()
        # 提交生成订单待支付
        # self.turl = host + 'hall/order/generateOrder'
        statmentorder_url = host + 'hall/order/calCourseCart'
        statmentorder_data = {
            "studentId": self.data['stus'],
            "couponIds": couponids,
            "classId": self.data['classid']
        }
        self.orderdata=statmentorder_data
        #print(orderdata)
        self.headers=self.data['heads']
        if bf=='true':
            all_locusts_spawned.wait()  # 集合点等待并发
            #print('------设置了集合点，并发执行------')
        else:
            pass
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        with self.client.post(path=statmentorder_url, data=json.dumps(self.orderdata),headers=self.headers,catch_response=True,verify=False) as self.checkresponse:
            contents = json.loads(self.checkresponse.text)
            if contents['code']==200:
                print('提交时间',nowtime,'学员stuid' ,self.data['stus'],'课程',self.data['classid'],'提交生成订单成功', contents)
                self.checkresponse.success()
                #self.data['reqtime']
            elif contents['code']==1000110010:
                print('提交时间',nowtime,'学员stuid' ,self.data['stus'],'课程',self.data['classid'],'提交订单数据过期', contents)
                self.checkresponse.failure('生成订单失败')
                #sys.exit()
            else:
                print('提交时间',nowtime,'学员stuid' ,self.data['stus'],'课程',self.data['classid'],'订单提交生成失败', contents)
                self.checkresponse.failure('生成订单失败')
                #sys.exit()
        #lock.release()

        if circle == 'true':
            self.user.user_data_queue.put_nowait(self.data)  # 把取出来的数据重新加入队列，如果不设置，队列取完后就停止
        else:
            exit(0)
        logger.get_requests_log(method='POST', path=apiurl, requests=self.orderdata, response=self.checkresponse.text)
        '''
        self.turl = host + 'hall/order/generateOrder'
        ordersub = {
            # "studentId": self.stuid
            "studentId": self.data['stus']
        }
        # self.headers = self.data['heads']
        with self.client.post(path=self.turl, data=json.dumps(ordersub), headers=self.headers, catch_response=True,
                              verify=False) as ordersubrsp:
            contents = json.loads(ordersubrsp.text)
            #print(contents)
        '''

    @task(20)  # 权重，数字越大占比越高
    def addinvoice(self):
        try:
            self.data = self.user.user_data_queue.get_nowait()  # 取值顺序
        except queue.Empty:  # 取不到数据时，走这里
            print('account data run out, test ended.')
            exit(0)
        #lock = Lock()
        #lock.acquire()
        # 提交生成订单待支付
        # self.turl = host + 'hall/order/generateOrder'
        self.turl = host + apiurl
        reqparams['studentId'] = self.data['stus']
        reqparams['orderId'] = orderid
        self.orderdata = reqparams
        #print(orderdata)
        self.headers = self.data['heads']
        if bf == 'true':
            all_locusts_spawned.wait()  # 集合点等待并发
        else:
            pass
        # print('------用户到达集合点了，开始执行------')
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        with self.client.post(path=self.turl, data=json.dumps(self.orderdata), headers=self.headers, catch_response=True,
                              verify=False) as self.checkresponse:
            contents = json.loads(self.checkresponse.text)
            if contents['code'] == 200:
                print('提交时间', nowtime, '学员stuid', self.data['stus'], '提交生成订单成功', contents)
                self.checkresponse.success()
            elif contents['code'] == 1000110010:
                print('提交时间', nowtime, '学员stuid', self.data['stus'], '提交数据过期', contents)
                self.checkresponse.failure('提交失败')
                # sys.exit()
            else:
                print( '提交时间', nowtime, '学员stuid', self.data['stus'], '提交生成失败', contents)
                self.checkresponse.failure('提交失败')
                # sys.exit()

        #lock.release()
        if circle == 'true':
            self.user.user_data_queue.put_nowait(self.data)  # 把取出来的数据重新加入队列，如果不设置，队列取完后就停止
        else:
            exit(0)
        logger.get_requests_log(method='POST', path=apiurl, requests=self.orderdata, response=self.checkresponse.text)
    def on_stop(self):
        print('------stop--------')

#class Websiteuser(HttpUser):
#FastHttpUser 请求高速模式用path=url，HttpUser低速用url
class Websiteuser(FastHttpUser):
    #tasks = [logintest]  # 必须以task_set属性开头，否则会报找不到类
    print('-----准备压测-----')
    tasks = [order]
    user_data_queue = queue.Queue(maxsize=-1)  # 创建队列，先进先出,设置队列长度
    #print(len(params))
    #多用户唯一取数压测，循环插入队列
    if len(params)>1:
        for head in params:
            for cls in classids:
                data = {
                        "stus": dict(head)['studentid'],
                        "classid": cls,
                        "heads": head
                        # "threads":heads.index(head) #获取索引
                        #"threads": params.index(params[0]), # 获取索引
                        }
                user_data_queue.put_nowait(data)  # 循环加入队列<全部>,循环完，继续执行
    #单用户循环压测
    else:
        # 单用户循环插入队列
        for ycnum in range(0,ycnums):
            #eg：循环取出班级id（读取配置文件yaml获得），如不需要删除该for语句
            for cls in classids:
                data = {
                    "stus": dict(params[0])['studentid'],
                    "heads": params[0],
                    #"threads": params.index(params[0]), # 获取索引
                    "classid": cls
                    }
                #print(data)
                user_data_queue.put_nowait(data)  # 循环加入队列<全部>,循环完，继续执行
    wait_time=between(1,2)#模拟用户在执行任务之间将等待时间
    host= host
    #host="http://172.16.0.168:8999"
    min_wait = 0  # 用户执行任务之间等待时间的下界，单位：毫秒;
    max_wait = 10  # 用户执行任务之间等待时间的上界，单位：毫秒;

if __name__=="__main__":
    #os.system("locust -f F:\pyproject\pxx\concurrencyorder.py --host=http://172.16.0.168:8999 --no-web  -c 1000 -r 10 --run-time 1m --loglever DEBUG --logfile order.log --csv=order")
    #os.system("locust -f F:\\pyproject\\pxx\\apporderlocust.py --web-host=0.0.0.0 --master --host=https://pxxapi-uat.zzpxx.com" )
    # 当前文件绝对路径
    p = os.path.abspath(__file__)
    os.system("locust -f %s --worker --master-host=172.16.0.131 " % p)
    #os.system("locust  --web-host=0.0.0.0 -f %s" % p)