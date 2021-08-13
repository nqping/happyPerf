#coding='utf-8'
import sys,os
sys.path.append(os.pardir)
os.path.abspath('..')
from gevent._semaphore import Semaphore
#from gevent import monkey
#monkey.patch_all(select=False)
from locust.contrib.fasthttp import FastHttpUser
import json,datetime
from locust import task, between,SequentialTaskSet,events, tag
import os,requests,ssl,random
import queue
from common import readconfig_ex,readenv,logger
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#import sys
#sys.setrecursionlimit(15000)
ssl._create_default_https_context = ssl._create_unverified_context
#host='https://bm-test.zzpxx.com/'
readcfg= readconfig_ex.readconfig('pcaddstu')
logintoken=readcfg['allparams']['x-token']
startlogintoken=logintoken[0]
endlogintoken=logintoken[-1]
loginmobile=readcfg['allparams']['telno']
startloginmobile=loginmobile[0]
endloginmobile=loginmobile[-1]
circle=readcfg['allparams']['iscircle']
bf=readcfg['allparams']['isbf']
grade=random.randint(1,9)
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
logger = logger.LocustLogger()
#logger.get_locust_Hook()
#创建集合点，当locust实例产生完成时触发（即所有用户启动完毕）
all_locusts_spawned = Semaphore()
all_locusts_spawned.acquire()
def on_hatch_complete(**kwargs):
    all_locusts_spawned.release()
#挂在到locust钩子函数（所有的Locust示例产生完成时触发）
events.spawning_complete.add_listener(on_hatch_complete)

class addstus(SequentialTaskSet):

    def on_start(self):

        print('-----star------')
        #self.index=0#定义移动下标的位置，每次都从0开始取值

    #@logouts('pc添加新学员')
    @task()#权重，数字越大占比越高
    @tag('注册添加学员','bm-test')
    def addstu(self):
        try:
            #get_nowait() 取不到数据直接崩溃；get() 取不到数据会一直等待
            data=self.user.user_data_queue.get_nowait()
        except queue.Empty:  # 取不到数据时，走这里
            print('account data run out, test ended.')
            exit(0)
        #print('orderbuy with stuid: {}, token: {}'.format(data['stus'], data['heads']['Authorization']))

        # 新增学员
        #self.turl=host+'api/a/student/addAndEditStudent'
        self.turl = host + apiurl
        reqparams['name']=data['name']
        reqparams['grade']=grade
        reqparams['mobile']=data['phone']
        reqparams['token']=data['token']
        reqparams['whetherBoy'] = True
        reqparams['motherSmsEnable']=True
        self.studata=reqparams
        if bf=='true':
            all_locusts_spawned.wait()  # 集合点等待并发
            #print('-----设置了集合点，并发执行-----')
        else:
            pass
        #print('------用户到达集合点了，开始执行------')
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        with self.client.post(path=self.turl,json=json.loads(json.dumps(self.studata),strict=False),catch_response=True,verify=False) as self.checkresponse:
            contents=json.loads(self.checkresponse.text)
            if contents['code']==10000:
                print('线程',data['threads'],data['phone'],'新增学员时间',nowtime,'学员手机号' ,data['phone'],'新增成功', contents)
                self.checkresponse.success()
            else:
                print('线程',data['threads'],data['phone'],'新增学员时间',nowtime,'学员手机号' ,data['phone'],'新增失败', contents)
                self.checkresponse.failure('新增失败')
                #sys.exit()

        if circle == 'true':
            self.user.user_data_queue.put_nowait(data)  # 把取出来的数据重新加入队列，如果不设置，队列取完后就停止
        else:
            exit(0)
        logger.get_requests_log(method='POST', path=apiurl, requests=self.studata, response=self.checkresponse.text)
    def on_stop(self):
        print('------stop--------')


#class Websiteuser(HttpUser):
#FastHttpUser 请求高速模式用path=url，HttpUser低速用url
class Websiteuser(FastHttpUser):
#class Websiteuser(HttpUser):
    #tasks = [logintest]  # 必须以task_set属性开头，否则会报找不到类
    tasks = [addstus]
    putdatas=[]
    for mobile in range(int(startloginmobile),int(endloginmobile)):
        #tokenlist=['1c0789b75d1f4666b8d3ff29315e35b5;:;1624416916657','e1659e031c1b40dabf625e003a18156a;:;1624417073640']
        tokenlist=logintoken
        #mobile=random.randint(19923191502,19923191999)
        names=''.join(random.sample('没人满后是他竟然同时将投入时间可以考虑的讨论权限撒村刷卡机低收入家庭因为不同职能部门内哦该螯合钙染膏该阿后继人家饿哦还让二号然而还让就让他我今天人生就是可是冉冉尔何如嗯嗯我刚好和任何人将统一洒欧莱雅集体股权按个人阿嘎加拿大班主任没什么明天就是瑞婆扣款',3))
        token=random.choice(tokenlist)
        datas={'mobile':mobile,'token':token,'name':names}
        putdatas.append(datas)
    user_data_queue = queue.Queue(maxsize=-1)  # 创建队列，先进先出,设置队列长度-1为无限
    #nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    for params in putdatas:
        datas = {
            "phone": dict(params)['mobile'],
            "token": dict(params)['token'],
            "name":dict(params)['name'],
            "threads": putdatas.index(params)
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
    p = os.path.abspath(__file__)
    os.system("locust --worker --master-host=172.16.0.131 -f %s" % p)
    #os.system("locust -f F:\\pyproject\\pxx\\pcaddstu.py  --master-host=172.16.0.168 --host=https://pxxapi-uat.zzpxx.com" )