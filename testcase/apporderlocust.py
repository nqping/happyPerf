#coding='utf-8'
import sys,os

sys.path.append(os.pardir)
os.path.abspath('../..')
from gevent._semaphore import Semaphore
#from gevent import monkey
#monkey.patch_all(select=False)
from locust.contrib.fasthttp import FastHttpUser
import json,datetime
from locust import task, between,SequentialTaskSet,events
import os,requests,ssl
import queue,re
from threading import Lock
from common import loginapp, readconfig_ex,loginappthread,logger,readenv,readexcel
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#import sys
#sys.setrecursionlimit(15000)
ssl._create_default_https_context = ssl._create_unverified_context
#host='https://pxxapi-test.zzpxx.com/'
#读取配置文件参数
readcfg= readconfig_ex.readconfig('apporderlocust')
loginmobile=readcfg['allparams']['telno']
startloginmobile=loginmobile[0]
endloginmobile=loginmobile[-1]
circle=readcfg['allparams']['iscircle']
bf=readcfg['allparams']['isbf']
env=readcfg['allparams']['env']
reqparams=readcfg['reqjson']
apiurl=readcfg['allparams']['apiurl']
productid=readcfg['allparams']['productid']
channel=readcfg['allparams']['channel']
try:
    ycnums=readcfg['allparams']['yctotals']
except (IOError,ValueError,KeyError) as e:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print(repr(e),exc_value,'配置文件yaml中未找到，取默认值100')
    ycnums=100
    pass
rdenv=readenv.readenv(channel)
# 判断压测环境test or uat
if env == 'test':
    host = rdenv[0]
elif env == 'uat':
    host = rdenv[1]
else:
    print('请正确填写测试的hostaddr--test or uat')
    exit(0)
#初始化登陆获取信息
#多线程登陆
params = loginappthread.mythreads(loginmobile,host,channel)
#单线程登陆
#params = loginapp.loginapp().login(loginmobile)
logger = logger.LocustLogger()
#logger.get_locust_Hook()
#创建集合点，当locust实例产生完成时触发（即所有用户启动完毕）
all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()
def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()
#挂在到locust钩子函数（所有的Locust示例产生完成时触发）
events.spawning_complete.add_listener(on_hatch_complete)
#TaskSet，所有用户按task权重比例压测
#class order(TaskSet):
#SequentialTaskSet，所有用户按task顺序压测，SequentialTaskSet是TaskSet子类，作用就是忽略权重，完全根据编写顺序来控制任务执行顺序，多用于事务压测
class order(SequentialTaskSet):
    def on_start(self):
        print('-----star------')

        try:
            # get_nowait() 取不到数据直接崩溃；get() 取不到数据会一直等待
            # data = self.user.user_data_queue.get_nowait()  # 取值顺序
            self.data = self.user.user_data_queue.get_nowait()  # 取值顺序

        except queue.Empty:  #  取不到数据时或设置的压测数据总数大于队列实际大小,退出程序
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
        if getcardrsp['code'] == 200 and productid in str(productId):
            print(self.data['stus'], '课程已在购课车，开始结算')
            self.statmentorder()
        else:
            # 添加购课车
            addcart_url = host + 'hall/courseCart/addAndEditCourseCart'
            self.carddata = {
                "studentId": self.data['stus'],
                "commodityId": productid  # 班级课程productid
            }
            cardreq = requests.post(url=addcart_url, data=json.dumps(self.carddata), headers=self.data['heads'],
                                    verify=False)
            cardrsp = cardreq.json()
            if cardrsp['code'] == 200:
                print(self.data['stus'], '添加购课车成功，开始结算')
                self.statmentorder()
                # return self.stuid, self.all_headers, self.mobile
            else:
                print(self.data['stus'], '添加购课车失败', cardrsp)
                # sys.exit()

    def statmentorder(self):
        statmentorder_url = host + 'hall/order/calCourseCart'
        statmentorder_data = {
            "studentId": self.data['stus']
        }
        requests.post(url=statmentorder_url, data=json.dumps(statmentorder_data), headers=self.data['heads'],
                      verify=False)

    @task(10)#权重，数字越大占比越高
    def suborder(self):
        '''
        try:
            # get_nowait() 取不到数据直接崩溃；get() 取不到数据会一直等待
            # data = self.user.user_data_queue.get_nowait()  # 取值顺序
            self.data = self.user.user_data_queue.get_nowait()  # 取值顺序
        except queue.Empty:  # 取不到数据时，走这里
            print('account data run out, test ended.')
            exit(0)
        '''
        #lock = Lock()
        #lock.acquire()
        # 提交生成订单待支付
        # self.turl = host + 'hall/order/generateOrder'
        self.turl = host + apiurl
        '''
        orderdata={
                    #"studentId": self.stuid
                    "studentId": data['stus']
                    }
        '''
        reqparams['studentId']=self.data['stus']
        orderdata=reqparams
        self.headers=self.data['heads']
        #是否并发，true并发，false不并发
        if bf=='true':
            all_locusts_spawned.wait()  # 集合点等待并发
            #print('------设置了集合点，并发执行------')
        else:
            pass
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        with self.client.post(path=self.turl, data=json.dumps(orderdata),headers=self.headers,catch_response=True,verify=False) as checkresponse:
            contents=json.loads(checkresponse.text)
            if contents['code']==200:
                print('线程',self.data['threads'],'提交时间',nowtime,'学员stuid' ,self.data['stus'],'提交生成订单成功', contents)
                checkresponse.success()
                #self.data['reqtime']
            elif contents['code']==1000110010:
                print('线程',self.data['threads'],'提交时间',nowtime,'学员stuid' ,self.data['stus'],'提交订单数据过期', contents)
                checkresponse.failure('生成订单失败')
                #sys.exit()
            else:
                print('线程',self.data['threads'],'提交时间',nowtime,'学员stuid' ,self.data['stus'],'订单提交生成失败', contents)
                checkresponse.failure('生成订单失败')
                #sys.exit()

        #lock.release()
        logger.get_requests_log(method='POST', path=apiurl, requests=orderdata, response=checkresponse.text)
        #是否循环取数，true循环，false不循环
        if circle == 'true':
            self.user.user_data_queue.put_nowait(self.data)  # 把取出来的数据重新加入队列，如果不设置，队列取完后就停止
        else:
            exit(0)
    def on_stop(self):
        print('------stop--------')

#class Websiteuser(HttpUser):
#FastHttpUser 请求高速模式用path=url，HttpUser低速用url
class Websiteuser(FastHttpUser):
    #tasks = [logintest]  # 必须以task_set属性开头，否则会报找不到类
    print('-----准备压测-----')
    tasks = [order]
    user_data_queue = queue.Queue(maxsize=-1)  # 创建队列，先进先出,设置队列长度
    for head in params:
        #nowtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        #nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        data = {
            "stus": dict(head)['studentid'],
            "heads": head,
            # "threads":heads.index(head) #获取索引
            "threads": params.index(head) # 获取索引
            #"reqtime":nowtime
            }
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
    os.system("locust  --worker --master-host=172.16.0.131 -f %s" % p)