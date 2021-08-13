#coding='utf-8'
import sys,os
sys.path.append(os.pardir)
#Semaphore对象内部管理一个计数器，该计数器由每个acquire()调用递减，并由每个release()调用递增。计数器永远不会低于零，当acquire()发现计数器为零时，线程阻塞，等待其他线程调用release()
from gevent._semaphore import Semaphore
#from gevent import monkey
#monkey.patch_all(select=False)
from locust.contrib.fasthttp import FastHttpUser
import json,datetime
from locust import task, between,SequentialTaskSet,events
import os,requests,ssl
import queue
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#import sys
#sys.setrecursionlimit(15000)
from common import readconfig_ex,logger,readenv

ssl._create_default_https_context = ssl._create_unverified_context
#host='https://pxxapi-test.zzpxx.com/'
readcfg= readconfig_ex.readconfig('registerlocust')
logintoken=readcfg['allparams']['x-token']
startlogintoken=logintoken[0]
endlogintoken=logintoken[1]
loginmobile=readcfg['allparams']['telno']
startloginmobile=loginmobile[0]
endloginmobile=loginmobile[-1]
circle=readcfg['allparams']['iscircle']
bf=readcfg['allparams']['isbf']
grade=readcfg['allparams']['grade']
env=readcfg['env']
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
logger = logger.LocustLogger()
logger.get_locust_Hook()
#创建集合点，当locust实例产生完成时触发（即所有用户启动完毕）
all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()
def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()
#挂在到locust钩子函数（所有的Locust示例产生完成时触发）
events.spawning_complete.add_listener(on_hatch_complete)
openheads = {
        # ":method": "POST",
        # ":path": "/oauth/send/code",
        # ":authority": "pxxapi-uat.zzpxx.com",
        # ":scheme": "https",
        "content-type": "application/json;charset=utf-8",
        "app-version": "1.3.0",
        "app-platform": "android",
        "app-id": "pxxedu",
        "app-channel": "official",
        "version": "v1",
        "client": "2",
        "user-agent": "okhttp/3.14.9",
        "small_version": "1",
        "content-type": "application/json; charset=utf-8"
    }
def getcode():
    datas=[]
    for mobile in range(startloginmobile, endloginmobile):
        # self.mobile=random.randint(19921391101,19921395999)
        # self.mobile=self.mobile+1
        url = host + 'oauth/send/code'
        codedata = {
            "phone": str(mobile)
            }
        #print(codedata)
        # req = sessions.post(url=url,data=json.dumps(self.codedata),headers=getheaders(),verify=False)
        req = requests.post(url=url, data=json.dumps(codedata), headers=openheads, verify=False)
        rsp = req.json()
        phonecode = rsp['data']['code']
        getdatas={"phone":str(mobile),"code":phonecode}
        datas.append(getdatas)
    print('----获取验证码完成-----')
    return datas
phonecode=getcode()
#print(phonecode)
#SequentialTaskSet是TaskSet子类，作用就是忽略权重，完全根据编写顺序来控制任务执行顺序，多用于事务压测
class registerapp(SequentialTaskSet):
    def on_start(self):
        print('-----star------')

    @task()#权重，数字越大占比越高
    def login(self):
        try:
            #get_nowait() 取不到数据直接崩溃；get() 取不到数据会一直等待
            #data = self.user.user_data_queue.get_nowait()  # 取值顺序
            #data = self.user_data_queue.get_nowait()  # 取值顺序
            data=self.user.user_data_queue.get_nowait()
        except queue.Empty:  # 取不到数据时，走这里
            print('account data run out, test ended.')
            exit(0)
        #print('orderbuy with stuid: {}, token: {}'.format(data['stus'], data['heads']['Authorization']))

        # 登陆
        #self.turl=host+'oauth/loginByCode'
        self.turl=host+apiurl
        '''
        login_data = {
            "phone": data['phone'],
            "code": data['code']
            }
        '''
        reqparams['phone']=data['phone']
        reqparams['code']=data['code']
        login_data=reqparams
        #print(login_data)
        if bf=='true':
            all_locusts_spawned.wait()  # 集合点等待并发
        else:
            pass
        #print('------用户到达集合点了，开始执行------')
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        with self.client.post(path=self.turl, data=json.dumps(login_data),headers=openheads,catch_response=True,verify=False) as checkresponse:
            contents=json.loads(checkresponse.text)
            if contents['code']==200:
                print('线程',data['threads'],'注册登陆时间',nowtime,'学员手机号' ,data['phone'],'注册登陆成功', contents)
                checkresponse.success()
            else:
                print('线程',data['threads'],'注册登陆时间',nowtime,'学员手机号' ,data['phone'],'注册登陆失败', contents)
                checkresponse.failure('注册失败')
                #sys.exit()
        logger.get_requests_log(method='POST', path=apiurl, requests=login_data, response=checkresponse.text)
        if circle == 'true':
            self.user.user_data_queue.put_nowait(data)  # 把取出来的数据重新加入队列，如果不设置，队列取完后就停止
        else:
            exit(0)

    def on_stop(self):
        print('------stop--------')

#class Websiteuser(HttpUser):
#FastHttpUser 请求高速模式用path=url，HttpUser低速用url
class Websiteuser(FastHttpUser):
#class Websiteuser(HttpUser):
    print('-----准备压测-----')
    #tasks = [logintest]  # 必须以task_set属性开头，否则会报找不到类
    tasks = [registerapp]
    user_data_queue = queue.Queue(maxsize=-1)  # 创建队列，先进先出,设置队列长度-1为无限
    #nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    for params in phonecode:
        datas = {
            "phone": dict(params)['phone'],
            "code": dict(params)['code'],
            "threads": phonecode.index(params)
            #"reqtime": nowtime
        }
        #print(datas)
        user_data_queue.put_nowait(datas)  # 循环加入队列<全部>,循环完，继续执行

    wait_time=between(1,2)#模拟用户在执行任务之间将等待时间
    host=host
    #host="http://172.16.0.168:8999"
    min_wait = 0  # 用户执行任务之间等待时间的下界，单位：毫秒;
    max_wait = 10  # 用户执行任务之间等待时间的上界，单位：毫秒;

if __name__=="__main__":
    #os.system("locust -f F:\pyproject\pxx\concurrencyorder.py --host=http://172.16.0.168:8999 --no-web  -c 1000 -r 10 --run-time 1m --loglever DEBUG --logfile order.log --csv=order")
    #os.system("locust -f F:\\pyproject\\pxx\\registerlocust.py --web-host=0.0.0.0 --host=https://pxxapi-uat.zzpxx.com" )
    p = os.path.abspath(__file__)
    os.system("locust -f %s --worker --master-host=172.16.0.131" % p)