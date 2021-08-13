#coding='utf-8'
import gevent
from gevent import monkey
monkey.patch_all()
#monkey.patch_all(select=False)
from gevent._semaphore import Semaphore
from common import logger
import sys,os,yaml,random
sys.setrecursionlimit(3000)#设置递归最大次数
sys.path.append(os.pardir)
os.path.abspath('..')
from locust.contrib.fasthttp import FastHttpUser
import json,datetime,time
from locust import TaskSet, task,HttpUser,between,SequentialTaskSet,events,user
import os,requests,ssl
import queue,re
from common import readconfig_ex,loginappthread,readenv
from threading import Lock
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#sys.setrecursionlimit(15000)
ssl._create_default_https_context = ssl._create_unverified_context
#host='https://pxxapi-test.zzpxx.com/'
readcfg=readconfig_ex.readconfig('getcoupon')
loginmobile=readcfg['allparams']['telno']
startloginmobile=loginmobile[0]
endloginmobile=loginmobile[-1]
circle=readcfg['allparams']['iscircle']
bf=readcfg['allparams']['isbf']
couponid=readcfg['allparams']['couponid']
#grade=readcfg['grade']
env=readcfg['allparams']['env']
reqparams=readcfg['reqjson']
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
#TaskSet，所有用户按task权重比例压测
#class order(TaskSet):
#SequentialTaskSet，所有用户按task顺序压测，SequentialTaskSet是TaskSet子类，作用就是忽略权重，完全根据编写顺序来控制任务执行顺序，多用于事务压测
class getcoupon(SequentialTaskSet):
    def on_start(self):
        print('-----star------')

    @task()#权重，数字越大占比越高
    def getcoupon(self):
        try:
            #get_nowait() 取不到数据直接崩溃；get() 取不到数据会一直等待
            #data = self.user.user_data_queue.get_nowait()  # 取值顺序
            data = self.user.user_data_queue.get_nowait()  # 取值顺序

        except queue.Empty:  # 取不到数据时，走这里
            print('account data run out, test ended.')
            #pass
            exit(0)
        lock=Lock()
        lock.acquire()
        # 提交生成订单待支付
        # self.turl = host + 'hall/order/generateOrder'
        self.turl = host + apiurl
        '''
        orderdata={
                    #"studentId": self.stuid
                    "studentId": data['stus']
                    }
        '''
        reqparams['studentId']=data['stus']
        #reqparams['_noShowLoading']=True
        reqparams['couponId']=couponid
        orderdata=reqparams
        #print(orderdata)
        #self.headers=data['heads']

        uagent=[
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0; Baiduspider-ads) Gecko/17.0 Firefox/17.0",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9b4) Gecko/2008030317 Firefox/3.0b4",
            "Mozilla/5.0 (Windows; U; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; BIDUBrowser 7.6)",
            "Mozilla/5.0 (Windows NT 6.3; WO=W64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.3; Win64; x64; Trident/7.0; Touch; LCJB; rv:11.0) like Gecko",
            'Mozilla/5.0 (Linux; Android 7.1.2; VOG-AL10 Build/HUAWEIVOG-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36 MMWEBID/179 MicroMessenger/8.0.3.1880(0x28000334) Process/tools WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm32'
            ]
        ips=[{'http':'45.250.226.53:8080'},{'http':'89.204.214.142:8080'},{'http':'185.238.239.29:8090'},{'http':'103.154.190.6:8080'},{'http':'103.233.154.242:8080'}]

        self.headers={
          'Authorization': data['heads']['Authorization'],
          'app-platform': '',
          'referer': 'https://sso-uat.zzpxx.com/choose_student',
          'app-channel': 'official',
          'version': 'v1',
          'client': '2',
          #'user-agent': 'Mozilla/5.0 (Linux; Android 7.1.2; VOG-AL10 Build/HUAWEIVOG-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36 MMWEBID/179 MicroMessenger/8.0.3.1880(0x28000334) Process/tools WeChat/arm32 Weixin NetType/WIFI Language/zh_CN ABI/arm32',
          'user-agent': random.choice(uagent),
          'studentid': data['stus'],
          'small_version': '0',
          'X-Requested-With': 'x-requested-with',
          'Content-Type': 'application/json'
        }
        if bf=='true':
            all_locusts_spawned.wait()  # 集合点等待并发
        else:
            pass
        #print('------用户到达集合点了，开始执行------')
        nowtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        with self.client.post(path=self.turl, data=json.dumps(orderdata),headers=self.headers,catch_response=True,verify=False,proxies=random.choice(ips)) as checkresponse:
            contents=json.loads(checkresponse.text)

            if contents['code']==200:
                print('线程',data['threads'],'提交时间',nowtime,'学员stuid' ,data['stus'],'提交成功', contents)
                checkresponse.success()

            elif contents['code']==1000110010:
                print('线程',data['threads'],'提交时间',nowtime,'学员stuid' ,data['stus'],'提交数据过期', contents)
                checkresponse.failure('返回失败')
                #sys.exit()
            else:
                print('线程',data['threads'],'提交时间',nowtime,'学员stuid' ,data['stus'],'提交失败', contents)
                checkresponse.failure('返回失败')
                #sys.exit()

        lock.release()
        logger.get_requests_log(method='POST', path=apiurl, requests=orderdata, response=checkresponse.text)
        #logger.info('请求地址%s,请求参数：%s' % (apiurl, orderdata))
        #logger.info('返回参数：%s' % checkresponse.text)
        if circle == 'true':
            self.user.user_data_queue.put_nowait(data)  # 把取出来的数据重新加入队列，如果不设置，队列取完后就停止
        else:
            exit(0)
    def on_stop(self):
        print('------stop--------')

#class Websiteuser(HttpUser):
#FastHttpUser 请求高速模式用path=url，HttpUser低速用url
class Websiteuser(FastHttpUser):
    #tasks = [logintest]  # 必须以task_set属性开头，否则会报找不到类
    print('-----准备压测-----')
    tasks = [getcoupon]
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
    #os.system("locust -f F:\\pyproject\\pxx\\testcase\\getcoupon.py --web-host=0.0.0.0 --master --host=https://pxxapi-uat.zzpxx.com" )
    p = os.path.abspath(__file__)
    os.system("locust  --worker --master-host=172.16.0.131 -f %s" % p)
