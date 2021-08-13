#coding='utf-8'
import sys,os,yaml,random
sys.path.append(os.pardir)
os.path.abspath('..')
from gevent._semaphore import Semaphore 
#from gevent import monkey
#monkey.patch_all(select=False)
from locust.contrib.fasthttp import FastHttpUser
import json,datetime,time
from locust import TaskSet, task,HttpUser,between,SequentialTaskSet,events,user
import os,requests,ssl
import queue,re
from threading import Lock
from common import readconfig_ex,loginapp,loginappthread,logger,readenv
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#import sys
#sys.setrecursionlimit(15000)
ssl._create_default_https_context = ssl._create_unverified_context
#host='https://pxxapi-test.zzpxx.com/'
#读取yaml配置文件，获取压测参数
readcfg=readconfig_ex.readconfig('searchclass')
loginmobile=readcfg['allparams']['telno']
startloginmobile=loginmobile[0]
endloginmobile=loginmobile[-1]
circle=readcfg['allparams']['iscircle']
bf=readcfg['allparams']['isbf']
env=readcfg['allparams']['env']
reqparams=readcfg['reqjson']
subject=random.choice(readcfg['allparams']['subject'])
grade=random.choice(readcfg['allparams']['grade'])
city=random.choice(readcfg['allparams']['cityid'])
apiurl=readcfg['allparams']['apiurl']
channel=readcfg['allparams']['channel']
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
logger.get_locust_Hook()
#创建集合点，当locust实例产生完成时触发（即所有用户启动完毕）
all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()
def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()
#挂在到locust钩子函数（所有的Locust示例产生完成时触发）
events.spawning_complete.add_listener(on_hatch_complete)
class searchclass(TaskSet):
    def on_start(self):
        print('-----star------')
    
    @task(20)#权重，数字越大占比越高
    def searchclass(self):
        try:
            self.data = self.user.user_data_queue.get_nowait()  # 取值顺序
        except queue.Empty:  # 取不到数据时，走这里
            print('account data run out, test ended.')
            exit(0)
        lock=Lock()
        lock.acquire()
        # 提交生成订单待支付
        # self.turl = host + 'hall/order/generateOrder'
        self.turl = host + apiurl
        #reqparams['cityId']=city
        #reqparams['subject']=subject
        #reqparams['grade']=grade
        orderdata=reqparams
        self.headers=self.data['heads']
        if bf=='true':
            all_locusts_spawned.wait()  # 集合点等待并发
        else:
            pass
        #print('------用户到达集合点了，开始执行------')
        nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        with self.client.post(path=self.turl, data=json.dumps(orderdata),headers=self.headers,catch_response=True,verify=False) as checkresponse:
            contents=json.loads(checkresponse.text)
            if contents['code']==200:
                print('线程',self.data['threads'],'提交时间',nowtime,'学员stuid' ,self.data['stus'],'提交成功', contents)
                checkresponse.success()
            elif contents['code']==1000110010:
                print('线程',self.data['threads'],'提交时间',nowtime,'学员stuid' ,self.data['stus'],'提交数据过期', contents)
                checkresponse.failure('提交失败')
                #sys.exit()
            else:
                print('线程',self.data['threads'],'提交时间',nowtime,'学员stuid' ,self.data['stus'],'提交失败', contents)
                checkresponse.failure('提交失败')
                #sys.exit()
        logger.get_requests_log(method='POST', path=apiurl, requests=orderdata, response=checkresponse.text)
        if circle=='true':
            self.user.user_data_queue.put_nowait(self.data)  # 把取出来的数据重新加入队列，如果不设置，队列取完后就停止
        else:
            pass
        lock.release()
    def on_stop(self):
        print('------stop--------')

class Websiteuser(FastHttpUser):
    print('-----准备压测-----')
    #tasks = [logintest]  # 必须以task_set属性开头，否则会报找不到类
    tasks = [searchclass]
    user_data_queue = queue.Queue(maxsize=-1)  # 创建队列，先进先出,设置队列长度
    for head in params:
        #nowtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        #nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        data = {
            "stus": dict(head)['studentid'],
            "heads": head,
            # "threads":heads.index(head) #获取索引
            "threads": params.index(head)  # 获取索引
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